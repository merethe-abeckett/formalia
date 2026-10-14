#!/usr/bin/env python3
"""Archive a statement after a deletion proposal's notice period has ended.

Moves Conjectures/<Name>/S<id>.lean and .json to Archive/<Name>/, keeps the id
(never reused), records why and where it was discussed, and stops it from
being built. Usage:
  scripts/archive_entry.py <Name> <id> --issue <url> --reason "<text>"
"""
import argparse, json, datetime, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conjecture"); ap.add_argument("id")
    ap.add_argument("--issue", required=True); ap.add_argument("--reason", required=True)
    a = ap.parse_args()
    d, n = a.id.split("-")
    stem = f"S{d}_{n}"
    src = ROOT / "Conjectures" / a.conjecture
    dst = ROOT / "Archive" / a.conjecture; dst.mkdir(parents=True, exist_ok=True)
    meta = json.loads((src / f"{stem}.json").read_text(encoding="utf-8"))
    meta["archived"] = {"at": datetime.date.today().isoformat(), "issue": a.issue, "reason": a.reason}
    (dst / f"{stem}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.move(str(src / f"{stem}.lean"), str(dst / f"{stem}.lean"))
    (src / f"{stem}.json").unlink()
    print(f"archived #{a.id} -> Archive/{a.conjecture}/{stem}.*")

if __name__ == "__main__":
    main()
