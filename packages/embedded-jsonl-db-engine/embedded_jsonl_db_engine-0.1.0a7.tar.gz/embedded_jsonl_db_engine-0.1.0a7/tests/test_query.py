from embedded_jsonl_db_engine import Database
from rich.console import Console
import sys
import os

_force_tty = os.environ.get("FORCE_TTY", "").lower() in ("1", "true", "yes", "on")
_isatty = getattr(sys.stderr, "isatty", lambda: False)()
_console = Console(file=sys.stderr, force_terminal=(_isatty or _force_tty), color_system="standard")
_tty_progress = os.environ.get("TTY_PROGRESS", "").lower() in ("1", "true", "yes", "on")

def progress_printer(evt):
    phase = evt.get("phase", "")
    pct = int(evt.get("pct", 0))
    msg = evt.get("msg", "")
    state = getattr(progress_printer, "_state", {"last": {}})
    last = state["last"]
    prev = last.get(phase, -1)
    is_tty = _tty_progress and getattr(_console, "is_terminal", False)

    if not is_tty:
        if pct in (0, 100) and (prev != pct):
            parts = [p for p in (phase, f"{pct}%", (f"- {msg}" if msg else "")) if p]
            _console.print("[progress] " + " ".join(parts))
        last[phase] = pct
        progress_printer._state = state
        return

    if pct < 100 and prev != -1 and (pct - prev) < 5:
        return
    parts = [p for p in (phase, f"{pct}%", (f"- {msg}" if (msg and pct in (0, 100)) else "")) if p]
    text = "[progress] " + " ".join(parts)
    _console.print("\r\x1b[2K" + text, end="")
    if pct >= 100:
        _console.print()
    last[phase] = pct
    progress_printer._state = state

def make_schema():
    return {
        "id":        {"type": "str", "mandatory": True, "index": True},
        "name":      {"type": "str", "mandatory": True, "index": True},
        "age":       {"type": "int", "default": 0, "index": True},
        "active":    {"type": "bool", "default": True},
        "createdAt": {"type": "datetime", "mandatory": True},
        "categories": {
            "type": "list", "items": {"type": "str"},
            "taxonomy": "categories", "taxonomy_mode": "multi",
            "strict": True, "index_membership": True
        }
    }

def test_projection_and_sorting(tmp_path):
    db_path = tmp_path / "users.jsonl"
    db = Database(str(db_path), schema=make_schema(), on_progress=progress_printer)

    # Prepare taxonomy key for strict validation
    db.taxonomy("categories").upsert("general")

    # Create few records
    names_ages = [("Alice", 25), ("Bob", 10), ("Charlie", 50)]
    ids = []
    for n, a in names_ages:
        r = db.new()
        r["name"] = n
        r["age"] = a
        r["categories"] = ["general"]
        r.save()
        ids.append(r.id)

    # Order by age desc and project fields
    it = db.find({"active": True}, order_by=[("age", "desc")], fields=["name"])
    lst = list(it)
    assert [rec["name"] for rec in lst] == ["Charlie", "Alice", "Bob"]
    # Projection keeps only requested fields + id
    assert set(lst[0].keys()) == {"name", "id"}
    assert "age" not in lst[0]

def test_nested_order_by(tmp_path):
    db_path = tmp_path / "users.jsonl"
    schema = make_schema()
    # Extend schema with nested object
    schema["profile"] = {"type": "object", "fields": {
        "score": {"type": "int", "default": 0, "index": True}
    }}
    db = Database(str(db_path), schema=schema, on_progress=progress_printer)
    db.taxonomy("categories").upsert("general")

    # Insert with nested profile.score
    vals = [3, 1, 2]
    for i, s in enumerate(vals):
        r = db.new()
        r["name"] = f"N{i}"
        r["profile"] = {"score": s}
        r["categories"] = ["general"]
        r.save()

    # Sort by nested path
    got = list(db.find({"active": True}, order_by=[("profile/score", "asc")], fields=["name", "profile"]))
    assert [rec["profile"]["score"] for rec in got] == [1, 2, 3]

def test_fast_projection_simple(tmp_path):
    db_path = tmp_path / "users.jsonl"
    db = Database(str(db_path), schema=make_schema(), on_progress=progress_printer)
    db.taxonomy("categories").upsert("general")

    # Insert records
    for i in range(5):
        r = db.new()
        r["name"] = f"N{i}"
        r["age"] = i * 10
        r["categories"] = ["general"]
        r.save()

    # Simple query with projection of scalar fields only
    lst = list(db.find({"age": {"$gte": 10}}, fields=["name", "age"]))
    assert all(set(rec.keys()) <= {"id", "name", "age"} for rec in lst)
    assert all(isinstance(rec["age"], int) for rec in lst)

def test_or_and_regex(tmp_path):
    db_path = tmp_path / "users.jsonl"
    db = Database(str(db_path), schema=make_schema(), on_progress=progress_printer)
    db.taxonomy("categories").upsert("general")

    # Insert records
    data = [("Alice", 25), ("Bob", 10), ("Charlie", 50)]
    for n, a in data:
        r = db.new()
        r["name"] = n
        r["age"] = a
        r["categories"] = ["general"]
        r.save()

    # Regex on name (case-insensitive)
    got = list(db.find({"name": {"$regex": "^al", "$flags": "i"}}))
    assert any(rec["name"] == "Alice" for rec in got)
    assert all(isinstance(rec["name"], str) for rec in got)

    # $or combining age==10 or name starting with Ch
    got2 = list(db.find({"$or": [{"age": {"$eq": 10}}, {"name": {"$regex": "^Ch"}}]}))
    names = {rec["name"] for rec in got2}
    assert names == {"Bob", "Charlie"}
