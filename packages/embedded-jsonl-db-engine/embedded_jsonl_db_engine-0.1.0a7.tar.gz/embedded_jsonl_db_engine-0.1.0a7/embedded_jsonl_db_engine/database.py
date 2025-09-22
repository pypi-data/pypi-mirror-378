from __future__ import annotations
import os
import json
import re
import io
import gzip
import shutil
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional, Tuple, Set
from .schema import Schema
from .taxonomy import TaxonomyAPI
from .index import InMemoryIndex, MetaEntry
from .storage import FileStorage
from .blobs import BlobManager
from .progress import Progress
from .fastregex import compile_path_pattern, extract_first
from .query import is_simple_query
from .utils import now_iso, canonical_json, sha256_hex, new_ulid, iso_to_epoch_ms
from .errors import ValidationError, ConflictError, IOCorruptionError, DuplicateIdError, SchemaError, LockError

# Scalar types used for building secondary indexes
_SCALAR_TYPES = {"str", "int", "float", "bool", "datetime"}

class Options:
    """
    Runtime options controlling lock retries and read-tail safety.
    """
    def __init__(
        self,
        process_lock_attempts: int = 40,
        process_lock_sleep_ms: int = 50,
        read_tail_retry_attempts: int = 40,
        read_tail_sleep_ms: int = 50,
        maintenance_attempts: int = 40,
        maintenance_sleep_ms: int = 50,
        allow_shared_read: bool = True,
        backup_root_dir: str = "embedded_jsonl_db_backup",
        backup_rolling_keep: int = 3,
        backup_daily_dir: str = "daily",
        backup_daily_keep: int = 7,
    ) -> None:
        self.process_lock_attempts = int(process_lock_attempts)
        self.process_lock_sleep_ms = int(process_lock_sleep_ms)
        self.read_tail_retry_attempts = int(read_tail_retry_attempts)
        self.read_tail_sleep_ms = int(read_tail_sleep_ms)
        self.maintenance_attempts = int(maintenance_attempts)
        self.maintenance_sleep_ms = int(maintenance_sleep_ms)
        self.allow_shared_read = bool(allow_shared_read)
        self.backup_root_dir = str(backup_root_dir)
        self.backup_rolling_keep = int(backup_rolling_keep)
        self.backup_daily_dir = str(backup_daily_dir)
        self.backup_daily_keep = int(backup_daily_keep)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "Options":
        if d is None:
            return cls()
        if isinstance(d, cls):
            return d  # type: ignore[return-value]
        if not isinstance(d, dict):
            return cls()
        return cls(
            process_lock_attempts=int(d.get("process_lock_attempts", 40)),
            process_lock_sleep_ms=int(d.get("process_lock_sleep_ms", 50)),
            read_tail_retry_attempts=int(d.get("read_tail_retry_attempts", 40)),
            read_tail_sleep_ms=int(d.get("read_tail_sleep_ms", 50)),
            maintenance_attempts=int(d.get("maintenance_attempts", 40)),
            maintenance_sleep_ms=int(d.get("maintenance_sleep_ms", 50)),
            allow_shared_read=bool(d.get("allow_shared_read", True)),
            backup_root_dir=str(d.get("backup_root_dir", "embedded_jsonl_db_backup")),
            backup_rolling_keep=int(d.get("backup_rolling_keep", 3)),
            backup_daily_dir=str(d.get("backup_daily_dir", "daily")),
            backup_daily_keep=int(d.get("backup_daily_keep", 7)),
        )

class TDBRecord(dict):
    """
    Dict-like record bound to a specific Database and id (after save()).
    Handles validation and tracks changes.
    """
    __slots__ = ("_db", "_id", "_meta_offset", "_orig_hash", "_dirty_fields", "_meta")

    def __init__(self, db: "Database", initial: Dict[str, Any]) -> None:
        super().__init__(initial)
        self._db = db
        self._id: Optional[str] = None
        self._meta_offset: Optional[int] = None
        self._orig_hash = self._hash_data()
        self._dirty_fields: set[str] = set()
        self._meta: Optional[Dict[str, Any]] = None

    def _hash_data(self) -> str:
        # Canonical JSON string is enough for dirty detection (sha256 not required here)
        return canonical_json(self)

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def meta(self) -> Optional[Dict[str, Any]]:
        return getattr(self, "_meta", None)

    @property
    def dirty(self) -> bool:
        return self._hash_data() != self._orig_hash

    @property
    def modified_fields(self) -> List[str]:
        return list(self._dirty_fields)

    def __setitem__(self, key: str, value: Any) -> None:
        self._db._validate_assign(key, value, self)
        super().__setitem__(key, value)
        self._dirty_fields.add(key)

    def save(self, force: bool = False) -> None:
        self._db._record_save(self, force=force)

    def reload(self) -> None:
        if not self._id:
            raise ValidationError("record has no id; save() it first")
        rec = self._db.get(self._id)
        if rec is None:
            raise ConflictError("record not found")
        super().clear()
        super().update(rec)
        self._orig_hash = self._hash_data()
        self._dirty_fields.clear()

class Database:
    def __init__(
        self,
        path: str,
        schema: Dict[str, Any],
        mode: str = "+",
        on_progress = None,
        maintenance: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.path = path
        self._schema = Schema(schema)
        self._target_schema_fields: Dict[str, Any] = json.loads(json.dumps(schema))
        self._taxonomies: Dict[str, Any] = { }
        self._fs = FileStorage(path)
        self._progress = Progress(on_progress)
        self._index = InMemoryIndex()
        self._maintenance = maintenance or {}
        self._header: Dict[str, Any] = {}
        # Runtime options and intra-process locks
        self.options = Options.from_dict(options)
        self._maint_lock = threading.Lock()
        self._maint_active = False
        self._write_lock = threading.RLock()
        # Precompute index specs from schema hints
        self._sec_paths: List[str] = []
        self._rev_list_paths: List[Tuple[str, str]] = []
        self._rev_single_paths: List[Tuple[str, str]] = []
        self._rev_map: Dict[str, str] = {}
        self._rev_list_strict: Dict[str, bool] = {}
        self._rev_single_strict: Dict[str, bool] = {}
        self._scalar_type_map: Dict[str, str] = {}
        self._compute_index_specs()
        self._open(mode)

    def _open(self, mode: str) -> None:
        """
        Open DB file: ensure header exists, scan meta to build in-memory index.
        Uses per-operation process-level locks with retries.
        """
        # Open file handle (no locking here)
        self._fs.open_exclusive(mode)
        # Emit only once per phase to keep single-line progress per process
        self._progress.emit("open.start", 0, path=self.path)

        # Read header under read lock; initialize if missing
        need_init = False
        _hdr = {}
        _schema_fields: Dict[str, Any] = {}
        taxonomies: Dict[str, Any] = {}
        try:
            with self._process_lock("read"):
                _hdr, _schema_fields, taxonomies = self._fs.read_header_and_schema()
        except IOCorruptionError:
            need_init = True

        if need_init:
            hdr = {
                "format": "ejl1",
                "table": os.path.splitext(os.path.basename(self.path))[0],
                "created": now_iso(),
                "defaults_always_materialized": True,
            }
            self._header = hdr
            self._taxonomies = {}
            # Write new header under write lock
            with self._process_lock("write"):
                self._fs.write_header_and_schema(hdr, self._schema._fields, self._taxonomies)
            self._compute_index_specs()
        else:
            # Keep taxonomies from file (schema migration may be needed)
            self._header = _hdr
            self._taxonomies = taxonomies or {}
            # If target schema differs from on-disk, run migration to target
            on_disk = _schema_fields
            if canonical_json(on_disk) != canonical_json(self._target_schema_fields):
                self._progress.emit("schema.migrate", 0, msg="Migrating schema")
                self._migrate_schema_to(self._target_schema_fields, old_fields=on_disk)
                return
            # Align schema to on-disk schema and recompute index specs
            self._schema = Schema(_schema_fields)
            self._compute_index_specs()

        # Rebuild in-memory index from meta stream (streaming, no full list to reduce memory)
        self._index = InMemoryIndex()
        try:
            total_bytes = os.path.getsize(self.path)
        except Exception:
            total_bytes = 0
        scanned = 0
        last_pct = -1
        # Hold a read lock for scanning (iter_meta_offsets also holds one defensively)
        with self._process_lock("read"):
            for offset, line in self._fs.iter_meta_offsets(
                attempts=self.options.read_tail_retry_attempts,
                sleep_ms=self.options.read_tail_sleep_ms,
            ):
                scanned += 1
                try:
                    meta = json.loads(line)
                except Exception:
                    continue
                if meta.get("_t") != "meta":
                    continue
                rec_id = meta.get("id")
                if not rec_id:
                    continue
                op = meta.get("op")
                ts_iso = meta.get("ts") or now_iso()
                ts_ms = iso_to_epoch_ms(ts_iso)
                offset_data = None
                if op == "put":
                    # Data line immediately follows meta line
                    offset_data = offset + len(line.encode("utf-8"))
                entry = MetaEntry(
                    id=rec_id,
                    offset_meta=offset,
                    offset_data=offset_data if op == "put" else None,
                    deleted=(op == "del"),
                    ts_ms=ts_ms,
                )
                self._index.add_meta(entry)
                if total_bytes:
                    pct = min(99, int((offset * 100) / max(1, total_bytes)))
                    if last_pct == -1 or pct - last_pct >= 5 or pct == 99:
                        self._progress.emit("open.scan_meta", pct, scanned=scanned, bytes_done=offset, bytes_total=total_bytes)
                        last_pct = pct
        # Finish scan phase once
        self._progress.emit("open.scan_meta", 100, scanned=scanned)

        # Build secondary & reverse indexes from live records
        self._progress.emit("open.build_indexes", 0, total=len(self._index.meta))
        with self._process_lock("read"):
            self._build_indexes_on_open()
        # NOTE: Performance notes (eng):
        # - Reopen and build indexes for 10k records ~0.47s on reference hardware (see tests).
        #   This phase streams meta to rebuild in-memory map and then optionally fast-extract scalars
        #   from JSON lines using regex to avoid full json.loads when no list-based taxonomy is present.
        # - Fast-plan query (>=5000) matched ~5000 in ~0.64s by extracting only needed scalar fields
        #   via regex and comparing without full parsing for non-matching records.
        # - Full-parse query with equivalent predicate via $or matched ~5000 in ~0.73s, as it requires
        #   json.loads for each candidate before evaluating predicates.
        self._progress.emit("open.done", 100, msg="Open complete")

    def new(self) -> TDBRecord:
        rec: Dict[str, Any] = {}
        self._schema.apply_defaults(rec)
        return TDBRecord(self, rec)

    def get(self, rec_id: str, *, include_meta: bool = False) -> TDBRecord | None:
        self._wait_for_maint()
        entry = self._index.meta.get(rec_id)
        if not entry or entry.deleted or entry.offset_data is None:
            return None
        line = self._fs.read_line_at(
            entry.offset_data,
            attempts=self.options.read_tail_retry_attempts,
            sleep_ms=self.options.read_tail_sleep_ms,
        )
        try:
            obj = json.loads(line)
        except Exception:
            return None
        # Optional integrity check against meta
        meta_obj = None
        try:
            meta_line = self._fs.read_line_at(
                entry.offset_meta,
                attempts=self.options.read_tail_retry_attempts,
                sleep_ms=self.options.read_tail_sleep_ms,
            )
            meta_obj = json.loads(meta_line)
            # Compare against data without trailing newline
            data_str_no_nl = line[:-1] if line.endswith("\n") else line
            data_bytes = data_str_no_nl.encode("utf-8")
            if "len_data" in meta_obj and meta_obj["len_data"] != len(data_bytes):
                raise IOCorruptionError("data length mismatch at read")
            if "sha256_data" in meta_obj:
                if meta_obj["sha256_data"] != sha256_hex(data_bytes):
                    raise IOCorruptionError("data hash mismatch at read")
        except IOCorruptionError:
            raise
        except Exception:
            # Ignore non-critical meta read/parse issues
            pass
        rec = TDBRecord(self, obj)
        rec._id = rec_id
        rec._meta_offset = entry.offset_meta
        rec._orig_hash = rec._hash_data()
        rec._dirty_fields.clear()
        if include_meta:
            rec._meta = meta_obj if isinstance(meta_obj, dict) else None
        return rec

    def find(
        self,
        query: Dict[str, Any],
        *,
        limit: Optional[int] = None,
        skip: int = 0,
        order_by: List[Tuple[str, str]] | None = None,
        fields: List[str] | None = None,
    ) -> Iterable[TDBRecord]:
        self._wait_for_maint()
        # Simple full-scan plan with basic predicate evaluation.
        # Supports:
        # - equality on scalars
        # - nested dicts like {"address": {"city": "Wien"}}
        # - simple ops: $eq/$ne/$gt/$gte/$lt/$lte
        # - $contains for list[str] or substring for str
        def is_op_key(k: str) -> bool:
            return k in ("$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$contains", "$in", "$nin", "$regex")

        def match_obj(obj: Dict[str, Any], q: Dict[str, Any]) -> bool:
            # Top-level $or support (disjunction). Other keys are ANDed with it.
            if "$or" in q:
                ors = q.get("$or")
                if not isinstance(ors, list) or not ors:
                    return False
                if not any(isinstance(sub, dict) and match_obj(obj, sub) for sub in ors):
                    return False
            for k, v in q.items():
                if k == "$or":
                    continue
                if k.startswith("$"):
                    return False  # unsupported top-level operators
                if isinstance(v, dict) and any(is_op_key(op) for op in v.keys()):
                    val = obj.get(k)
                    for op, arg in v.items():
                        if op == "$flags":
                            # Used together with $regex; ignore here
                            continue
                        if op == "$eq":
                            if val != arg:
                                return False
                        elif op == "$ne":
                            if val == arg:
                                return False
                        elif op == "$gt":
                            try:
                                if not (val > arg):
                                    return False
                            except Exception:
                                return False
                        elif op == "$gte":
                            try:
                                if not (val >= arg):
                                    return False
                            except Exception:
                                return False
                        elif op == "$lt":
                            try:
                                if not (val < arg):
                                    return False
                            except Exception:
                                return False
                        elif op == "$lte":
                            try:
                                if not (val <= arg):
                                    return False
                            except Exception:
                                return False
                        elif op == "$in":
                            if not isinstance(arg, list):
                                return False
                            if isinstance(val, list):
                                if not any(x in arg for x in val):
                                    return False
                            else:
                                if val not in arg:
                                    return False
                        elif op == "$nin":
                            if not isinstance(arg, list):
                                return False
                            if isinstance(val, list):
                                if any(x in arg for x in val):
                                    return False
                            else:
                                if val in arg:
                                    return False
                        elif op == "$contains":
                            if isinstance(val, list):
                                if arg not in val:
                                    return False
                            elif isinstance(val, str):
                                if str(arg) not in val:
                                    return False
                            else:
                                return False
                        elif op == "$regex":
                            if not isinstance(val, str):
                                return False
                            flags_val = 0
                            try:
                                flags_str = v.get("$flags", "")
                                if isinstance(flags_str, str):
                                    if "i" in flags_str:
                                        flags_val |= re.IGNORECASE
                                    if "m" in flags_str:
                                        flags_val |= re.MULTILINE
                                    if "s" in flags_str:
                                        flags_val |= re.DOTALL
                                pattern = re.compile(str(arg), flags_val)
                            except Exception:
                                return False
                            if not pattern.search(val):
                                return False
                        else:
                            return False
                elif isinstance(v, dict):
                    sub = obj.get(k)
                    if not isinstance(sub, dict):
                        return False
                    if not match_obj(sub, v):
                        return False
                else:
                    if obj.get(k) != v:
                        return False
            return True

        # Prefilter with in-memory indexes where possible
        cand_ids = self._prefilter_ids(query)
        if cand_ids is None:
            items_iter = self._index.meta.items()
        else:
            items_iter = ((rid, self._index.meta.get(rid)) for rid in cand_ids)

        # Decide if we can use Fast plan (regex extraction) to avoid json.loads on non-matching records
        use_fast = is_simple_query(query)

        # Extract simple terms (path, op, arg)
        terms: List[Tuple[str, str, Any]] = []
        def walk_terms(obj: Dict[str, Any], base: Tuple[str, ...]) -> None:
            for k, v in obj.items():
                if k.startswith("$"):
                    continue
                new_base = base + (k,)
                if isinstance(v, dict):
                    ops = [op for op in v.keys() if isinstance(op, str) and op.startswith("$")]
                    if ops:
                        if "$eq" in v:
                            terms.append(("/".join(new_base), "$eq", v["$eq"]))
                        if "$ne" in v:
                            terms.append(("/".join(new_base), "$ne", v["$ne"]))
                        if "$gt" in v:
                            terms.append(("/".join(new_base), "$gt", v["$gt"]))
                        if "$gte" in v:
                            terms.append(("/".join(new_base), "$gte", v["$gte"]))
                        if "$lt" in v:
                            terms.append(("/".join(new_base), "$lt", v["$lt"]))
                        if "$lte" in v:
                            terms.append(("/".join(new_base), "$lte", v["$lte"]))
                        if "$in" in v:
                            terms.append(("/".join(new_base), "$in", v["$in"]))
                        if "$nin" in v:
                            terms.append(("/".join(new_base), "$nin", v["$nin"]))
                    else:
                        walk_terms(v, new_base)
                else:
                    terms.append(("/".join(new_base), "$eq", v))
        walk_terms(query, ())

        # Build regex patterns if fast is eligible and all paths map to known scalar types
        pat_map: Dict[str, Any] = {}
        if use_fast:
            for path, _op, _arg in terms:
                tp = self._scalar_type_map.get(path)
                if tp is None:
                    use_fast = False
                    break
                if path not in pat_map:
                    pat_map[path] = (tp, compile_path_pattern(path, tp))
        # Prepare fast projection (optional) for scalar fields and simple order_by
        can_fast_project = False
        proj_pat_map: Dict[str, Any] = {}
        need_fields: Set[str] = set()
        if use_fast and fields is not None:
            can_fast_project = True
            for f in fields:
                if "/" in f or f not in self._scalar_type_map:
                    can_fast_project = False
                    break
                need_fields.add(f)
            if can_fast_project and order_by:
                for of, _dir in order_by:
                    if "/" in of or of not in self._scalar_type_map:
                        can_fast_project = False
                        break
                    need_fields.add(of)
            if can_fast_project and need_fields:
                for p in need_fields:
                    tp2 = self._scalar_type_map[p]
                    proj_pat_map[p] = (tp2, compile_path_pattern(p, tp2))

        recs: List[TDBRecord] = []
        for rec_id, entry in items_iter:
            if not entry or entry.deleted or entry.offset_data is None:
                continue
            line = self._fs.read_line_at(
                entry.offset_data,
                attempts=self.options.read_tail_retry_attempts,
                sleep_ms=self.options.read_tail_sleep_ms,
            )
            # Integrity check against meta; skip corrupt records
            try:
                meta_line = self._fs.read_line_at(
                    entry.offset_meta,
                    attempts=self.options.read_tail_retry_attempts,
                    sleep_ms=self.options.read_tail_sleep_ms,
                )
                meta_obj = json.loads(meta_line)
                data_str_no_nl = line[:-1] if line.endswith("\n") else line
                data_bytes = data_str_no_nl.encode("utf-8")
                if "len_data" in meta_obj and meta_obj["len_data"] != len(data_bytes):
                    continue
                if "sha256_data" in meta_obj and meta_obj["sha256_data"] != sha256_hex(data_bytes):
                    continue
            except Exception:
                # On errors reading meta, proceed without skipping
                pass

            matched = True
            if use_fast and terms:
                def parse_val(tp: str, s: Optional[str]):
                    if s is None:
                        return None
                    try:
                        if tp == "str" or tp == "datetime":
                            return json.loads(s)
                        if tp == "int":
                            return int(s)
                        if tp == "float":
                            return float(s)
                        if tp == "bool":
                            return True if s == "true" else False
                    except Exception:
                        return None
                    return None
                def cmp(op: str, val, arg) -> bool:
                    try:
                        if op == "$eq":
                            return val == arg
                        if op == "$ne":
                            return val != arg
                        if op == "$gt":
                            return val > arg
                        if op == "$gte":
                            return val >= arg
                        if op == "$lt":
                            return val < arg
                        if op == "$lte":
                            return val <= arg
                        if op == "$in":
                            return isinstance(arg, list) and (val in arg)
                        if op == "$nin":
                            return isinstance(arg, list) and (val not in arg)
                        return False
                    except Exception:
                        return False
                for path, op, arg in terms:
                    tp, pat = pat_map[path]
                    raw = extract_first(pat, line)
                    val = parse_val(tp, raw)
                    # Normalize arg to same type (supports scalars and $in/$nin lists)
                    try:
                        if op in ("$in", "$nin") and isinstance(arg, list):
                            coerced = []
                            for av in arg:
                                if tp == "int":
                                    coerced.append(int(av))
                                elif tp == "float":
                                    coerced.append(float(av))
                                elif tp in ("str", "datetime"):
                                    coerced.append(str(av))
                                elif tp == "bool":
                                    if isinstance(av, str):
                                        coerced.append(av.lower() == "true")
                                    else:
                                        coerced.append(bool(av))
                                else:
                                    coerced.append(av)
                            arg = coerced
                        else:
                            if tp == "int" and not isinstance(arg, int):
                                arg = int(arg)
                            elif tp == "float" and not isinstance(arg, (int, float)):
                                arg = float(arg)
                            elif tp in ("str", "datetime") and not isinstance(arg, str):
                                arg = str(arg)
                            elif tp == "bool" and not isinstance(arg, bool):
                                if isinstance(arg, str):
                                    arg = (arg.lower() == "true")
                                else:
                                    arg = bool(arg)
                    except Exception:
                        matched = False
                        break
                    if val is None and op not in ("$ne",):
                        matched = False
                        break
                    if not cmp(op, val, arg):
                        matched = False
                        break
                if not matched:
                    continue
                # For matched fast-path records, materialize object for result/ordering/projection
                obj = None
                if can_fast_project and proj_pat_map:
                    obj_dict: Dict[str, Any] = {}
                    for p, (ptp, ppat) in proj_pat_map.items():
                        rawp = extract_first(ppat, line)
                        valp = parse_val(ptp, rawp)
                        if valp is not None:
                            obj_dict[p] = valp
                    # Always include id for downstream projection/sorting
                    obj_dict["id"] = rec_id
                    obj = obj_dict
                else:
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
            else:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not match_obj(obj, query):
                    continue

            rec = TDBRecord(self, obj)
            rec._id = rec_id
            rec._meta_offset = entry.offset_meta
            rec._orig_hash = rec._hash_data()
            rec._dirty_fields.clear()
            recs.append(rec)

        # Sorting
        if order_by:
            def norm(v):
                if v is None:
                    return ("", "")
                if isinstance(v, (int, float, bool)):
                    return ("0", str(v))
                if isinstance(v, str):
                    return ("1", v)
                try:
                    return ("2", json.dumps(v, sort_keys=True, ensure_ascii=False))
                except Exception:
                    return ("2", str(v))
            def get_by_path(r: Dict[str, Any], p: str):
                if "/" in p:
                    return self._extract_at_path(r, p)
                return r.get(p)
            for field, direction in reversed(order_by):
                reverse = (str(direction).lower() == "desc")
                recs.sort(key=lambda r: norm(get_by_path(r, field)), reverse=reverse)

        # Skip / limit
        start = max(0, int(skip)) if isinstance(skip, int) else 0
        if limit is None:
            selected = recs[start:]
        else:
            selected = recs[start:start + int(limit)]
        for r in selected:
            if fields:
                field_set = set(fields)
                field_set.add("id")
                obj = {k: r.get(k) for k in field_set if k in r}
                r2 = TDBRecord(self, obj)
                r2._id = r.id
                r2._meta_offset = r._meta_offset
                r2._orig_hash = r2._hash_data()
                r2._dirty_fields.clear()
                yield r2
            else:
                yield r

    def update(self, query: Dict[str, Any], patch: Dict[str, Any]) -> int:
        n = 0
        self._progress.emit("update.start", 0)
        for rec in self.find(query):
            self._deep_update(rec, patch)
            rec.save()
            n += 1
            if n % 100 == 0:
                self._progress.emit("update.run", 0, updated=n)
        self._progress.emit("update.done", 100, updated=n)
        return n

    def delete(self, query: Dict[str, Any]) -> int:
        """
        Logical deletion: append meta(op:"del") for matched records and update index.
        """
        # Wait if maintenance is active
        self._wait_for_maint()

        n = 0
        self._progress.emit("delete.start", 0)
        for rec in self.find(query):
            if not rec._id:
                continue
            with self._write_lock:
                with self._process_lock("write"):
                    # Remove record from secondary/reverse indexes before marking deleted
                    self._index_remove_from_obj(rec._id, rec)
                    ts_iso = now_iso()
                    meta = {"id": rec._id, "op": "del", "ts": ts_iso}
                    off_meta, _ = self._fs.append_meta_data(meta, None)
                    entry = MetaEntry(
                        id=rec._id,
                        offset_meta=off_meta,
                        offset_data=None,
                        deleted=True,
                        ts_ms=iso_to_epoch_ms(ts_iso),
                    )
                    self._index.add_meta(entry)
                    n += 1
                    if n % 100 == 0:
                        self._progress.emit("delete.run", 0, deleted=n)
        self._progress.emit("delete.done", 100, deleted=n)
        return n

    # ----- Index helpers -----

    def _prefilter_ids(self, query: Dict[str, Any]) -> Optional[Set[str]]:
        """
        Use in-memory indexes to preselect candidate ids.
        Supports:
          - equality on scalar indexed paths
          - equality on single-taxonomy string paths
          - $contains on list[str] taxonomy paths
        Returns:
          - set of ids if at least one indexable predicate found
          - None otherwise (caller should full-scan)
        """
        terms: List[Tuple[str, str, Any]] = []

        def walk(obj: Dict[str, Any], base: Tuple[str, ...]) -> None:
            for k, v in obj.items():
                if k.startswith("$"):
                    continue
                new_base = base + (k,)
                if isinstance(v, dict):
                    ops = [op for op in v.keys() if isinstance(op, str) and op.startswith("$")]
                    if ops:
                        if "$eq" in v:
                            terms.append(("/".join(new_base), "$eq", v["$eq"]))
                        if "$in" in v:
                            terms.append(("/".join(new_base), "$in", v["$in"]))
                        if "$contains" in v:
                            terms.append(("/".join(new_base), "$contains", v["$contains"]))
                    else:
                        walk(v, new_base)
                else:
                    terms.append(("/".join(new_base), "$eq", v))

        walk(query, ())

        candidate_ids: Optional[Set[str]] = None

        for path, op, arg in terms:
            ids: Optional[Set[str]] = None
            if op == "$eq":
                if path in self._sec_paths:
                    key = self._canonicalize_value(arg)
                    ids = set(self._index.secondary.get((path, key), set()))
                elif path in self._rev_map:
                    taxo = self._rev_map[path]
                    ids = set(self._index.reverse.get((taxo, str(arg)), set()))
            elif op == "$in":
                if isinstance(arg, list):
                    union_ids: Set[str] = set()
                    if path in self._sec_paths:
                        for av in arg:
                            key = self._canonicalize_value(av)
                            union_ids |= self._index.secondary.get((path, key), set())
                        ids = set(union_ids)
                    elif path in self._rev_map:
                        taxo = self._rev_map[path]
                        for av in arg:
                            union_ids |= self._index.reverse.get((taxo, str(av)), set())
                        ids = set(union_ids)
            elif op == "$contains":
                if path in self._rev_map:
                    taxo = self._rev_map[path]
                    ids = set(self._index.reverse.get((taxo, str(arg)), set()))
            if ids is not None:
                candidate_ids = ids if candidate_ids is None else (candidate_ids & ids)
                if candidate_ids is not None and len(candidate_ids) == 0:
                    break

        return candidate_ids

    def _compute_index_specs(self) -> None:
        # Build lists of paths for secondary and reverse indexes based on schema hints
        self._sec_paths.clear()
        self._rev_list_paths.clear()
        self._rev_single_paths.clear()
        self._rev_map.clear()
        self._rev_list_strict.clear()
        self._rev_single_strict.clear()
        self._scalar_type_map.clear()
        flat = getattr(self._schema, "_flat", {})
        for path_tuple, fspec in flat.items():
            path = "/".join(path_tuple)
            t = getattr(fspec, "type", None)
            if not path or not t:
                continue
            if t in _SCALAR_TYPES:
                self._scalar_type_map[path] = t
                if getattr(fspec, "index", False):
                    self._sec_paths.append(path)
            if t == "list" and getattr(fspec, "index_membership", False) and getattr(fspec, "taxonomy", None):
                taxo = getattr(fspec, "taxonomy")
                self._rev_list_paths.append((path, taxo))
                self._rev_map[path] = taxo
                self._rev_list_strict[path] = bool(getattr(fspec, "strict", False))
            if t in ("str",) and getattr(fspec, "taxonomy", None) and getattr(fspec, "taxonomy_mode", None) == "single":
                taxo = getattr(fspec, "taxonomy")
                self._rev_single_paths.append((path, taxo))
                self._rev_map[path] = taxo
                self._rev_single_strict[path] = bool(getattr(fspec, "strict", False))

    def _build_indexes_on_open(self) -> None:
        """
        Build in-memory indexes after meta scan.
        Optimized path: if there are no list-based taxonomy fields, extract scalar values via fast regex
        without full JSON parsing. Otherwise, fall back to full JSON parsing to handle membership lists.
        """
        # If there are no list-based taxonomy paths, we can avoid full JSON parse
        if not self._rev_list_paths:
            # Prepare patterns for scalar secondary indexes
            pat_map: Dict[str, Tuple[str, Any]] = {}
            for path in self._sec_paths:
                tp = self._scalar_type_map.get(path)
                if tp:
                    pat_map[path] = (tp, compile_path_pattern(path, tp))
            # Prepare patterns for single-string taxonomy refs
            single_map: Dict[str, Tuple[str, Any, str]] = {}
            for path, taxo in self._rev_single_paths:
                tp = self._scalar_type_map.get(path, "str")
                single_map[path] = (tp, compile_path_pattern(path, tp), taxo)

            def parse_val(tp: str, s: Optional[str]):
                if s is None:
                    return None
                try:
                    if tp == "str" or tp == "datetime":
                        return json.loads(s)
                    if tp == "int":
                        return int(s)
                    if tp == "float":
                        return float(s)
                    if tp == "bool":
                        return True if s == "true" else False
                except Exception:
                    return None
                return None

            total = len(self._index.meta)
            built = 0
            for rid, ent in self._index.meta.items():
                if ent.deleted or ent.offset_data is None:
                    continue
                line = self._fs.read_line_at(
                    ent.offset_data,
                    attempts=self.options.read_tail_retry_attempts,
                    sleep_ms=self.options.read_tail_sleep_ms,
                )
                # Secondary scalar indexes
                for path, (tp, pat) in pat_map.items():
                    raw = extract_first(pat, line)
                    val = parse_val(tp, raw)
                    if isinstance(val, (str, int, float, bool)):
                        self._index.add_secondary(path, self._canonicalize_value(val), rid)
                # Single taxonomy refs
                for path, (tp, pat, taxo) in single_map.items():
                    raw = extract_first(pat, line)
                    val = parse_val(tp, raw)
                    if isinstance(val, str):
                        self._index.add_reverse(taxo, val, rid)
                built += 1
                if built % 100 == 0:
                    self._progress.emit("open.build_indexes", int(built * 100 / max(1, total)), built=built)
            # Emit final progress once
            self._progress.emit("open.build_indexes", 100, built=built)
            return

        # Fallback: need full JSON to process list-based taxonomy memberships
        built = 0
        total = len(self._index.meta)
        for rid, ent in self._index.meta.items():
            if ent.deleted or ent.offset_data is None:
                continue
            try:
                obj_line = self._fs.read_line_at(ent.offset_data)
                obj = json.loads(obj_line)
            except Exception:
                continue
            self._index_add_from_obj(rid, obj)
            built += 1
            if built % 100 == 0:
                self._progress.emit("open.build_indexes", int(built * 100 / max(1, total)), built=built)
        # Emit final progress once for fallback path
        self._progress.emit("open.build_indexes", 100, built=built)

    def _extract_at_path(self, obj: Dict[str, Any], path: str):
        cur: Any = obj
        for key in (p for p in path.split("/") if p):
            if not isinstance(cur, dict) or key not in cur:
                return None
            cur = cur[key]
        return cur

    def _canonicalize_value(self, v: Any) -> str:
        return canonical_json(v)

    def _index_add_from_obj(self, rec_id: str, obj: Dict[str, Any]) -> None:
        # Secondary scalar indexes
        for path in self._sec_paths:
            v = self._extract_at_path(obj, path)
            if isinstance(v, (str, int, float, bool)):
                self._index.add_secondary(path, self._canonicalize_value(v), rec_id)
        # Reverse taxonomy for list
        for path, taxo in self._rev_list_paths:
            lst = self._extract_at_path(obj, path)
            if isinstance(lst, list):
                for item in lst:
                    if isinstance(item, str):
                        self._index.add_reverse(taxo, item, rec_id)
        # Reverse taxonomy for single scalar
        for path, taxo in self._rev_single_paths:
            val = self._extract_at_path(obj, path)
            if isinstance(val, str):
                self._index.add_reverse(taxo, val, rec_id)

    def _index_remove_from_obj(self, rec_id: str, obj: Dict[str, Any]) -> None:
        # Secondary scalar indexes
        for path in self._sec_paths:
            v = self._extract_at_path(obj, path)
            if isinstance(v, (str, int, float, bool)):
                self._index.remove_secondary(path, self._canonicalize_value(v), rec_id)
        # Reverse taxonomy for list
        for path, taxo in self._rev_list_paths:
            lst = self._extract_at_path(obj, path)
            if isinstance(lst, list):
                for item in lst:
                    if isinstance(item, str):
                        self._index.remove_reverse(taxo, item, rec_id)
        # Reverse taxonomy for single scalar
        for path, taxo in self._rev_single_paths:
            val = self._extract_at_path(obj, path)
            if isinstance(val, str):
                self._index.remove_reverse(taxo, val, rec_id)

    def _set_at_path(self, obj: Dict[str, Any], path: str, value: Any) -> bool:
        cur: Any = obj
        parts = [p for p in path.split("/") if p]
        if not parts:
            return False
        for key in parts[:-1]:
            if not isinstance(cur, dict) or key not in cur:
                return False
            cur = cur[key]
        if not isinstance(cur, dict):
            return False
        cur[parts[-1]] = value
        return True

    def _delete_at_path(self, obj: Dict[str, Any], path: str) -> bool:
        cur: Any = obj
        parts = [p for p in path.split("/") if p]
        if not parts:
            return False
        for key in parts[:-1]:
            if not isinstance(cur, dict) or key not in cur:
                return False
            cur = cur[key]
        if isinstance(cur, dict) and parts[-1] in cur:
            del cur[parts[-1]]
            return True
        return False

    def _transform_taxonomy_in_obj(self, obj: Dict[str, Any], *, list_paths: List[str], scalar_paths: List[str], mapping: Dict[str, Optional[str]]) -> None:
        # Transform list[str] taxonomy memberships
        for path in list_paths:
            v = self._extract_at_path(obj, path)
            if isinstance(v, list):
                new_list: List[str] = []
                seen = set()
                changed = False
                for item in v:
                    if isinstance(item, str):
                        if item in mapping:
                            new_item = mapping[item]
                            changed = True
                            if new_item is None:
                                continue
                            item = new_item
                    if isinstance(item, str) and item not in seen:
                        seen.add(item)
                        new_list.append(item)
                if changed:
                    self._set_at_path(obj, path, new_list)
        # Transform single string taxonomy refs
        for path in scalar_paths:
            v = self._extract_at_path(obj, path)
            if isinstance(v, str) and v in mapping:
                new_val = mapping[v]
                if new_val is None:
                    self._delete_at_path(obj, path)
                else:
                    self._set_at_path(obj, path, new_val)

    def taxonomy(self, name: str) -> TaxonomyAPI:
        return TaxonomyAPI(self, name)

    @contextmanager
    def _process_lock(self, kind: str):
        """
        Process-level lock context manager: "read" | "write" | "maint".
        """
        ok = self._fs.acquire_lock(
            "maint" if kind == "maint" else ("write" if kind == "write" else "read"),
            attempts=self.options.process_lock_attempts,
            sleep_ms=self.options.process_lock_sleep_ms,
            allow_shared_read=self.options.allow_shared_read,
        )
        if not ok:
            raise LockError(f"Failed to acquire {kind} lock after {self.options.process_lock_attempts} attempts")
        try:
            yield
        finally:
            self._fs.release_lock()

    def _wait_for_maint(self) -> None:
        """
        Block reads/writes while maintenance is active in this process.
        """
        for _ in range(max(1, self.options.maintenance_attempts)):
            if not self._maint_active:
                return
            time.sleep(max(0, self.options.maintenance_sleep_ms) / 1000.0)
        raise LockError("Maintenance lock wait timed out")

    def _taxonomy_header_update(self, name: str, *, op: str, key: str, attrs: Dict[str, Any]) -> None:
        """
        Update taxonomy metadata in header only (no data migration). Rewrites header and rebuilds indexes.
        Supported ops: "upsert", "set_attrs".
        """
        if not name or not isinstance(name, str):
            raise ValidationError("taxonomy name must be non-empty string")
        if not key or not isinstance(key, str):
            raise ValidationError("taxonomy key must be non-empty string")

        # Block all operations in-process and hold an exclusive process lock
        with self._maint_lock:
            self._maint_active = True
            try:
                taxo = self._taxonomies.setdefault(name, {"list": []})
                items = taxo.get("list")
                if not isinstance(items, list):
                    items = []
                    taxo["list"] = items

                idx = None
                for i, item in enumerate(items):
                    if isinstance(item, dict) and item.get("key") == key:
                        idx = i
                        break

                if op == "upsert":
                    if idx is not None:
                        # merge attrs into existing
                        cur = dict(items[idx])
                        cur.update(attrs or {})
                        cur["key"] = key
                        items[idx] = cur
                    else:
                        new_item = {"key": key}
                        if attrs:
                            new_item.update(attrs)
                        items.append(new_item)
                elif op == "set_attrs":
                    if idx is None:
                        raise ValidationError("taxonomy key not found for set_attrs")
                    cur = dict(items[idx])
                    cur.update(attrs or {})
                    cur["key"] = key
                    items[idx] = cur
                else:
                    raise ValidationError(f"unsupported taxonomy header op: {op!r}")

                # Rewrite header safely (close handle to avoid appending to unlinked inode)
                with self._process_lock("maint"):
                    self._fs.close()
                    self._fs.rewrite_header(self._header, self._schema._fields, self._taxonomies)
                # Reopen and rebuild indexes (offsets changed after header rewrite)
                self._open("+")
            finally:
                self._maint_active = False

    def _taxonomy_migrate(self, name: str, **kwargs: Any) -> None:
        """
        Perform full-file rewrite to apply taxonomy key changes across records.
        Supported actions:
          - action="rename", old_key, new_key, collision="merge"
          - action="merge", source_keys: List[str], target_key: str
          - action="delete", key: str, strategy="detach"
        """
        action = kwargs.get("action")
        if action not in ("rename", "merge", "delete"):
            raise ValidationError("unsupported taxonomy migration action")

        # Block all operations in-process and hold an exclusive process lock
        with self._maint_lock:
            self._maint_active = True
            try:
                taxo = self._taxonomies.setdefault(name, {"list": []})
                items = taxo.get("list") or []
                if not isinstance(items, list):
                    items = []
                items_by_key = {item.get("key"): dict(item) for item in items if isinstance(item, dict) and "key" in item}

                mapping: Dict[str, Optional[str]] = {}

                if action == "rename":
                    old_key = kwargs.get("old_key")
                    new_key = kwargs.get("new_key")
                    collision = kwargs.get("collision", "merge")
                    if not old_key or not new_key:
                        raise ValidationError("rename requires old_key and new_key")
                    mapping[old_key] = new_key
                    if collision != "merge" and new_key in items_by_key and old_key in items_by_key:
                        raise ValidationError("rename collision not supported other than 'merge'")
                    if old_key in items_by_key:
                        src = items_by_key.pop(old_key)
                        if new_key not in items_by_key:
                            src["key"] = new_key
                            items_by_key[new_key] = src

                elif action == "merge":
                    source_keys = kwargs.get("source_keys") or []
                    target_key = kwargs.get("target_key")
                    if not isinstance(source_keys, list) or not target_key:
                        raise ValidationError("merge requires source_keys list and target_key")
                    for sk in source_keys:
                        if sk == target_key:
                            continue
                        mapping[sk] = target_key
                    if target_key not in items_by_key:
                        items_by_key[target_key] = {"key": target_key}
                    for sk in source_keys:
                        items_by_key.pop(sk, None)

                elif action == "delete":
                    key = kwargs.get("key")
                    strategy = kwargs.get("strategy", "detach")
                    if not key:
                        raise ValidationError("delete requires key")
                    if strategy != "detach":
                        raise ValidationError("only 'detach' delete strategy is supported")
                    mapping[key] = None
                    items_by_key.pop(key, None)

                # Update in-memory taxonomies before migration
                new_items = list(items_by_key.values())
                self._taxonomies[name] = {"list": new_items}

                # Determine schema paths referencing this taxonomy
                list_paths = [p for (p, t) in self._rev_list_paths if t == name]
                scalar_paths = [p for (p, t) in self._rev_single_paths if t == name]

                # Close handle, then rewrite file under exclusive process lock
                with self._process_lock("maint"):
                    self._fs.close()

                    tmp_path = f"{self.path}.migrate.tmp"
                    with open(tmp_path, "w", encoding="utf-8", newline="\n") as dst:
                        # Write header with updated taxonomies
                        header_lines = [
                            {"_t": "header", **self._header},
                            {"_t": "schema", "fields": self._schema._fields},
                            {"_t": "taxonomies", "items": self._taxonomies},
                            {"_t": "begin"},
                        ]
                        for obj in header_lines:
                            dst.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")

                        # Copy and transform live records by ts order
                        live_entries = [e for e in self._index.meta.values() if (not e.deleted) and (e.offset_data is not None)]
                        live_entries.sort(key=lambda e: e.ts_ms)
                        total = len(live_entries)
                        for i, e in enumerate(live_entries, 1):
                            line = self._fs.read_line_at(
                                e.offset_data,
                                attempts=self.options.read_tail_retry_attempts,
                                sleep_ms=self.options.read_tail_sleep_ms,
                            )
                            try:
                                obj = json.loads(line)
                            except Exception:
                                continue
                            self._transform_taxonomy_in_obj(obj, list_paths=list_paths, scalar_paths=scalar_paths, mapping=mapping)
                            data_str = canonical_json(obj)
                            data_bytes = data_str.encode("utf-8")
                            ts_iso = now_iso()
                            meta_obj = {
                                "_t": "meta",
                                "id": e.id,
                                "op": "put",
                                "ts": ts_iso,
                                "len_data": len(data_bytes),
                                "sha256_data": sha256_hex(data_bytes),
                            }
                            dst.write(json.dumps(meta_obj, ensure_ascii=False, separators=(",", ":")) + "\n")
                            dst.write(data_str + "\n")
                            self._progress.emit("taxonomy.migrate", int(i * 100 / max(1, total)), key=name, action=action)

                        dst.flush()
                        try:
                            os.fsync(dst.fileno())
                        except Exception:
                            pass

                    self._fs.replace_file(tmp_path)
                self._open("+")
            finally:
                self._maint_active = False

    def _migrate_schema_to(self, new_fields: Dict[str, Any], old_fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Full-file rewrite to switch schema to new_fields.
        Applies defaults of the new schema and validates each record.
        Disallows incompatible type changes (e.g., int -> str) on existing fields.
        """
        self._progress.emit("schema.migrate", 0, msg="Starting schema migration")
        # Use provided old_fields (on-disk) or current in-memory schema as a baseline
        base_old_fields = old_fields or self._schema._fields
        sch_new = Schema(new_fields)
        sch_old = Schema(base_old_fields)
        # Detect type changes on overlapping field paths
        def _typemap(sch: Schema) -> Dict[str, str]:
            return {"/".join(p): fs.type for p, fs in getattr(sch, "_flat", {}).items()}
        t_old = _typemap(sch_old)
        t_new = _typemap(sch_new)
        for path, old_t in t_old.items():
            if path in t_new:
                new_t = t_new[path]
                if new_t != old_t:
                    raise SchemaError(f"schema type change for field '{path}': {old_t} -> {new_t} is not supported")

        # Block all operations in-process and hold an exclusive process lock
        with self._maint_lock:
            self._maint_active = True
            try:
                with self._process_lock("maint"):
                    # Close handle to avoid writing to unlinked inode during replace
                    self._fs.close()

                    tmp_path = f"{self.path}.schemamigrate.tmp"
                    with open(tmp_path, "w", encoding="utf-8", newline="\n") as dst:
                        # Write header with updated schema
                        header_lines = [
                            {"_t": "header", **self._header},
                            {"_t": "schema", "fields": new_fields},
                            {"_t": "taxonomies", "items": self._taxonomies},
                            {"_t": "begin"},
                        ]
                        for obj in header_lines:
                            dst.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")

                        # Build live entries by streaming meta (self._index is not built yet on fresh open)
                        live_map: Dict[str, MetaEntry] = {}
                        for offset, mline in self._fs.iter_meta_offsets(
                            attempts=self.options.read_tail_retry_attempts,
                            sleep_ms=self.options.read_tail_sleep_ms,
                        ):
                            try:
                                m = json.loads(mline)
                            except Exception:
                                continue
                            if m.get("_t") != "meta":
                                continue
                            rid = m.get("id")
                            if not isinstance(rid, str) or not rid:
                                continue
                            op = m.get("op")
                            ts_iso = m.get("ts") or now_iso()
                            ts_ms = iso_to_epoch_ms(ts_iso)
                            off_data = offset + len(mline.encode("utf-8")) if op == "put" else None
                            live_map[rid] = MetaEntry(
                                id=rid, offset_meta=offset, offset_data=off_data, deleted=(op == "del"), ts_ms=ts_ms
                            )

                        live_entries = [e for e in live_map.values() if (not e.deleted) and (e.offset_data is not None)]
                        live_entries.sort(key=lambda e: e.ts_ms)
                        total = len(live_entries)
                        for i, e in enumerate(live_entries, 1):
                            line = self._fs.read_line_at(
                                e.offset_data,
                                attempts=self.options.read_tail_retry_attempts,
                                sleep_ms=self.options.read_tail_sleep_ms,
                            )
                            try:
                                obj = json.loads(line)
                            except Exception:
                                continue
                            # Apply defaults of new schema and validate
                            sch_new.apply_defaults(obj)
                            sch_new.validate(obj)

                            data_str = canonical_json(obj)
                            data_bytes = data_str.encode("utf-8")
                            ts_iso = now_iso()
                            meta_obj = {
                                "_t": "meta",
                                "id": e.id,
                                "op": "put",
                                "ts": ts_iso,
                                "len_data": len(data_bytes),
                                "sha256_data": sha256_hex(data_bytes),
                            }
                            dst.write(json.dumps(meta_obj, ensure_ascii=False, separators=(",", ":")) + "\n")
                            dst.write(data_str + "\n")
                            self._progress.emit("schema.migrate", int(i * 100 / max(1, total)), migrated=i, total=total)

                        dst.flush()
                        try:
                            os.fsync(dst.fileno())
                        except Exception:
                            pass

                    # Replace file and reopen (will rebuild indexes against the new schema)
                    self._fs.replace_file(tmp_path)
                # Update in-memory schema to the new one for subsequent operations
                self._schema = Schema(new_fields)
                self._compute_index_specs()
                self._open("+")
                self._progress.emit("schema.migrate", 100, msg="Schema migration complete")
            finally:
                self._maint_active = False

    def compact_now(self) -> None:
        """
        Rewrite file to remove garbage records based on current in-memory index.
        Runs only if garbage_ratio >= 0.30.
        """
        # Compute garbage ratio as (total_meta - live_count) / total_meta
        total_meta = 0
        for _ in self._fs.iter_meta_offsets(
            attempts=self.options.read_tail_retry_attempts,
            sleep_ms=self.options.read_tail_sleep_ms,
        ):
            total_meta += 1
        live_entries = [e for e in self._index.meta.values() if (not e.deleted) and (e.offset_data is not None)]
        live_count = len(live_entries)
        if total_meta <= 0:
            return
        garbage_ratio = (total_meta - live_count) / max(1, total_meta)
        if garbage_ratio < 0.30:
            return

        self._progress.emit("compact.start", 0, msg="Starting compaction", total_meta=total_meta, live=live_count)

        # Block all operations in-process and hold an exclusive process lock
        with self._maint_lock:
            self._maint_active = True
            try:
                with self._process_lock("maint"):
                    # Close file handle to ensure stable rename on replace
                    self._fs.close()

                    tmp_path = f"{self.path}.compact.tmp"
                    with open(tmp_path, "w", encoding="utf-8", newline="\n") as dst:
                        # Write header
                        lines = [
                            {"_t": "header", **self._header},
                            {"_t": "schema", "fields": self._schema._fields},
                            {"_t": "taxonomies", "items": self._taxonomies},
                            {"_t": "begin"},
                        ]
                        for obj in lines:
                            s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                            dst.write(s + "\n")

                        # Copy live records in file order to minimize seeks. No JSON parse.
                        live_entries_sorted = sorted(live_entries, key=lambda e: (e.offset_data or 0))
                        total = len(live_entries_sorted)
                        with open(self.path, "rb") as src:
                            for i, e in enumerate(live_entries_sorted, 1):
                                if e.offset_data is None:
                                    continue
                                src.seek(e.offset_data)
                                line_bytes = src.readline()
                                try:
                                    data_str = line_bytes.decode("utf-8")
                                except UnicodeDecodeError:
                                    # Replace invalid bytes to keep compaction robust
                                    data_str = line_bytes.decode("utf-8", errors="replace")
                                # Remove trailing newline for len/hash calculation
                                data_str_no_nl = data_str[:-1] if data_str.endswith("\n") else data_str
                                data_bytes = data_str_no_nl.encode("utf-8")
                                ts_iso = now_iso()
                                meta_obj = {
                                    "_t": "meta",
                                    "id": e.id,
                                    "op": "put",
                                    "ts": ts_iso,
                                    "len_data": len(data_bytes),
                                    "sha256_data": sha256_hex(data_bytes),
                                }
                                dst.write(json.dumps(meta_obj, ensure_ascii=False, separators=(",", ":")) + "\n")
                                dst.write(data_str_no_nl + "\n")
                                self._progress.emit("compact.copy", int(i * 100 / max(1, total)), copied=i, total=total)

                        dst.flush()
                        try:
                            os.fsync(dst.fileno())
                        except Exception:
                            pass

                    # Atomically replace and reopen
                    self._fs.replace_file(tmp_path)
                self._open("+")
                self._progress.emit("compact.done", 100, msg="Compaction complete", live=live_count)
            finally:
                self._maint_active = False

    def backup_now(self, kind: str = "rolling") -> None:
        """
        Create backups: rolling (.bak.N) or daily gz snapshot.
        """
        backup_conf = self._maintenance.get("backup", {}) if isinstance(self._maintenance, dict) else {}
        keep = int(backup_conf.get("rolling_keep", self.options.backup_rolling_keep))
        daily_dirname = str(backup_conf.get("daily_dir", self.options.backup_daily_dir))

        root_dir_name = str(self.options.backup_root_dir)
        root_dir = os.path.join(os.path.dirname(os.path.abspath(self.path)), root_dir_name)
        os.makedirs(root_dir, exist_ok=True)

        # Ensure data is flushed by closing handle temporarily
        self._fs.close()

        base = os.path.basename(self.path)

        if kind == "rolling":
            with self._maint_lock:
                self._maint_active = True
                try:
                    with self._process_lock("maint"):
                        self._progress.emit("backup.rolling", 0, msg="Rolling backup")
                        # Rotate .bak.N files
                        last_path = os.path.join(root_dir, f"{base}.bak.{keep}")
                        if os.path.exists(last_path):
                            try:
                                os.remove(last_path)
                            except Exception:
                                pass
                        for i in range(keep, 1, -1):
                            src = os.path.join(root_dir, f"{base}.bak.{i-1}")
                            dst = os.path.join(root_dir, f"{base}.bak.{i}")
                            if os.path.exists(src):
                                try:
                                    os.replace(src, dst)
                                except Exception:
                                    try:
                                        shutil.copy2(src, dst)
                                        os.remove(src)
                                    except Exception:
                                        pass
                        dest1 = os.path.join(root_dir, f"{base}.bak.1")
                        with open(self.path, "rb") as src_f, open(dest1, "wb") as dst_f:
                            shutil.copyfileobj(src_f, dst_f, length=1024 * 1024)
                            dst_f.flush()
                            try:
                                os.fsync(dst_f.fileno())
                            except Exception:
                                pass
                        self._progress.emit("backup.rolling", 100, msg="Rolling backup complete", path=dest1)
                finally:
                    self._maint_active = False

        elif kind == "daily":
            with self._maint_lock:
                self._maint_active = True
                try:
                    with self._process_lock("maint"):
                        self._progress.emit("backup.daily", 0, msg="Daily backup")
                        daily_dir = os.path.join(root_dir, daily_dirname)
                        os.makedirs(daily_dir, exist_ok=True)
                        date_str = now_iso().split("T", 1)[0]
                        dest = os.path.join(daily_dir, f"{base}.{date_str}.jsonl.gz")
                        if os.path.exists(dest):
                            self._progress.emit("backup.daily", 100, msg="Daily backup exists", path=dest)
                        else:
                            with open(self.path, "rb") as src_f, gzip.open(dest, "wb") as gz:
                                shutil.copyfileobj(src_f, gz, length=1024 * 1024)
                                try:
                                    gz.flush()
                                except Exception:
                                    pass
                            self._progress.emit("backup.daily", 100, msg="Daily backup complete", path=dest)
                        # Retention: keep only last N daily backups
                        daily_keep = int(backup_conf.get("daily_keep", self.options.backup_daily_keep))
                        try:
                            all_files = sorted(os.listdir(daily_dir))
                            # match files of this DB only
                            pat = re.compile(re.escape(base) + r"\.\d{4}-\d{2}-\d{2}\.jsonl\.gz\Z")
                            own_files = [f for f in all_files if pat.match(f)]
                            if len(own_files) > daily_keep:
                                to_delete = own_files[:-daily_keep]
                                for fn in to_delete:
                                    try:
                                        os.remove(os.path.join(daily_dir, fn))
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                finally:
                    self._maint_active = False
        else:
            raise ValidationError(f"Unknown backup kind: {kind!r}")

        # Reacquire file handle (no locking) for subsequent operations
        self._fs.open_exclusive("+")

    def put_blob(self, stream_or_bytes, *, mime: str, filename: str | None = None) -> Dict[str, Any]:
        """
        Store a BLOB in external CAS and return a reference dict.
        Accepts bytes or a binary file-like object.
        """
        mgr = BlobManager(self.path)
        if isinstance(stream_or_bytes, (bytes, bytearray)):
            bio = io.BytesIO(stream_or_bytes)
            return mgr.put_blob(bio, mime, filename)
        if hasattr(stream_or_bytes, "read"):
            return mgr.put_blob(stream_or_bytes, mime, filename)
        raise ValidationError("put_blob expects bytes or a binary stream")

    def open_blob(self, ref: Dict[str, Any]):
        """
        Open blob by reference for reading.
        """
        mgr = BlobManager(self.path)
        return mgr.open_blob(ref)

    def gc_blobs(self) -> Dict[str, int]:
        """
        Garbage-collect orphaned blobs based on references in live records.
        """
        self._wait_for_maint()
        # Collect referenced hashes from all live records
        def collect(obj, out: Set[str]) -> None:
            if isinstance(obj, dict):
                if "$blob" in obj and isinstance(obj.get("$blob"), str) and obj["$blob"].startswith("sha256:"):
                    out.add(obj["$blob"].split("sha256:", 1)[1])
                for v in obj.values():
                    collect(v, out)
            elif isinstance(obj, list):
                for it in obj:
                    collect(it, out)

        used: Set[str] = set()
        for e in self._index.meta.values():
            if e.deleted or e.offset_data is None:
                continue
            try:
                line = self._fs.read_line_at(
                    e.offset_data,
                    attempts=self.options.read_tail_retry_attempts,
                    sleep_ms=self.options.read_tail_sleep_ms,
                )
                obj = json.loads(line)
            except Exception:
                continue
            collect(obj, used)

        mgr = BlobManager(self.path)
        removed, freed = mgr.gc(used)
        return {"files_removed": removed, "bytes_freed": freed}

    def close(self) -> None:
        """
        Close underlying file handle.
        """
        self._fs.close()

    def stats(self) -> Dict[str, int]:
        """
        Return basic database statistics.
        """
        live = 0
        deleted = 0
        for e in self._index.meta.values():
            if e.deleted:
                deleted += 1
            elif e.offset_data is not None:
                live += 1
        sec_entries = sum(len(s) for s in self._index.secondary.values())
        rev_entries = sum(len(s) for s in self._index.reverse.values())
        return {
            "live": live,
            "deleted": deleted,
            "secondary_index_entries": sec_entries,
            "reverse_index_entries": rev_entries,
        }

    def _validate_taxonomies_strict(self, obj: Dict[str, Any]) -> None:
        """
        Enforce taxonomy constraints for strict fields:
        - list[str] taxonomy with strict=True: all items must exist in taxonomy list
        - single str taxonomy with strict=True: value must exist in taxonomy list
        Also validates item types (list elements are strings).
        """
        # Build allowed sets lazily
        allowed_cache: Dict[str, Set[str]] = {}

        def allowed_keys(taxo: str) -> Set[str]:
            if taxo not in allowed_cache:
                items = self._taxonomies.get(taxo, {}).get("list", [])
                keys = {it.get("key") for it in items if isinstance(it, dict) and "key" in it}
                allowed_cache[taxo] = {k for k in keys if isinstance(k, str)}
            return allowed_cache[taxo]

        # list[str] strict
        for path, taxo in self._rev_list_paths:
            strict = self._rev_list_strict.get(path, False)
            if not strict:
                continue
            v = self._extract_at_path(obj, path)
            if v is None:
                continue
            if not isinstance(v, list):
                raise ValidationError(f"taxonomy list path '{path}' must be list[str]")
            allow = allowed_keys(taxo)
            for item in v:
                if not isinstance(item, str):
                    raise ValidationError(f"taxonomy list path '{path}' must contain strings")
                if item not in allow:
                    raise ValidationError(f"unknown taxonomy key '{item}' for '{taxo}' at '{path}'")

        # single str strict
        for path, taxo in self._rev_single_paths:
            strict = self._rev_single_strict.get(path, False)
            if not strict:
                continue
            v = self._extract_at_path(obj, path)
            if v is None:
                continue
            if not isinstance(v, str):
                raise ValidationError(f"taxonomy single path '{path}' must be string")
            allow = allowed_keys(taxo)
            if v not in allow:
                raise ValidationError(f"unknown taxonomy key '{v}' for '{taxo}' at '{path}'")

    def _validate_assign(self, key: str, value: Any, rec: Dict[str, Any]) -> None:
        # Full validation will run in save(); keep minimal checks here.
        return

    def _record_save(self, rec: TDBRecord, *, force: bool) -> None:
        # Wait if maintenance is active
        self._wait_for_maint()

        with self._write_lock:
            with self._process_lock("write"):
                # Assign/align id and createdAt on new records
                if rec._id is None:
                    # If user pre-filled "id" field, respect it; otherwise generate new ULID
                    pre_id = rec.get("id")
                    if isinstance(pre_id, str) and pre_id:
                        rec._id = pre_id
                    else:
                        rec._id = new_ulid()
                        rec["id"] = rec._id
                    if "createdAt" not in rec:
                        rec["createdAt"] = now_iso()
                else:
                    # Ensure the data field "id" matches internal _id
                    if rec.get("id") != rec._id:
                        rec["id"] = rec._id

                if not force and not rec.dirty:
                    return

                # Optimistic concurrency: ensure we save over the latest version
                if rec._id is not None and rec._meta_offset is not None:
                    cur = self._index.meta.get(rec._id)
                    if cur and cur.offset_meta != rec._meta_offset:
                        raise ConflictError("record was modified by another operation")

                # Duplicate id guard on first insert
                existing = self._index.meta.get(rec._id) if rec._id is not None else None
                if rec._meta_offset is None and existing and not existing.deleted:
                    raise DuplicateIdError(f"record with id '{rec._id}' already exists")

                # Full validation
                self._schema.validate(rec)
                # Enforce taxonomy strictness (if enabled in schema)
                self._validate_taxonomies_strict(rec)

                # Remove old index entries if any
                old_entry = self._index.meta.get(rec._id) if rec._id else None
                if old_entry and not old_entry.deleted and old_entry.offset_data is not None:
                    try:
                        old_line = self._fs.read_line_at(
                            old_entry.offset_data,
                            attempts=self.options.read_tail_retry_attempts,
                            sleep_ms=self.options.read_tail_sleep_ms,
                        )
                        old_obj = json.loads(old_line)
                        self._index_remove_from_obj(rec._id, old_obj)
                    except Exception:
                        pass

                # Serialize and compute meta
                data_str = canonical_json(dict(rec))
                data_bytes = data_str.encode("utf-8")
                ts_iso = now_iso()
                meta = {
                    "id": rec._id,
                    "op": "put",
                    "ts": ts_iso,
                    "len_data": len(data_bytes),
                    "sha256_data": sha256_hex(data_bytes),
                }

                # Append and get offsets
                off_meta, off_data = self._fs.append_meta_data(meta, data_str)

                # Update index
                entry = MetaEntry(
                    id=rec._id,
                    offset_meta=off_meta,
                    offset_data=off_data,
                    deleted=False,
                    ts_ms=iso_to_epoch_ms(ts_iso),
                )
                self._index.add_meta(entry)

                # Update secondary/reverse indexes for new content
                self._index_add_from_obj(rec._id, rec)

                # Sync state
                rec._meta_offset = off_meta
                rec._orig_hash = rec._hash_data()
                rec._dirty_fields.clear()

    @staticmethod
    def _deep_update(rec: Dict[str, Any], patch: Dict[str, Any]) -> None:
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(rec.get(k), dict):
                Database._deep_update(rec[k], v)
            else:
                rec[k] = v
