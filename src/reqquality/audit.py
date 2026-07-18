"""Hash-chained audit log for repeatable analysis runs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_record(path: str | Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one hash-chained audit record."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = _last_hash(target)
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "previous_hash": previous_hash, "record": record}
    payload["hash"] = _hash_payload(payload)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
    return payload


def verify_log(path: str | Path) -> dict[str, Any]:
    """Verify hash chaining for the audit log."""
    target = Path(path)
    if not target.exists():
        return {"valid": True, "records": 0}
    previous = "GENESIS"
    records = 0
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            expected = payload["hash"]
            actual = _hash_payload({k: v for k, v in payload.items() if k != "hash"})
            if expected != actual or payload["previous_hash"] != previous:
                return {"valid": False, "records": records}
            previous = expected
            records += 1
    return {"valid": True, "records": records}


def _last_hash(path: Path) -> str:
    if not path.exists():
        return "GENESIS"
    last = ""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            last = line
    if not last:
        return "GENESIS"
    return str(json.loads(last)["hash"])


def _hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
