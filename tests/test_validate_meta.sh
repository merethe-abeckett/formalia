#!/usr/bin/env bash
# 表述编号全库唯一、永不复用的测试：bash tests/test_validate_meta.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fails=0
setup() {
  rm -rf "$T/r"; mkdir -p "$T/r/Conjectures"
  cp -r "$ROOT/scripts" "$T/r/scripts"
  cp -r "$ROOT/Conjectures/Goldbach" "$T/r/Conjectures/Goldbach"
}
# 把 Goldbach 的 #20261014-01 复制成另一个猜想下的同号条目
dup_into() {
  local d="$T/r/Conjectures/$1"; mkdir -p "$d"
  python3 -I - "$T/r/Conjectures/Goldbach" "$d" "$1" <<'PY'
import json, sys, shutil
from pathlib import Path
src, dst, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
c = json.loads((src / "conjecture.json").read_text(encoding="utf-8")); c["slug"] = name.lower()
(dst / "conjecture.json").write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
m = json.loads((src / "S20261014_01.json").read_text(encoding="utf-8"))
m["conjecture"] = name.lower(); m["module"] = f"Conjectures.{name}.S20261014_01"
(dst / "S20261014_01.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
shutil.copy(src / "S20261014_01.lean", dst / "S20261014_01.lean")
PY
}
expect() {  # expect <ok|fail> <描述> [<输出须含的文字>]
  local out rc=0; out="$(python3 "$T/r/scripts/validate_meta.py" 2>&1)" || rc=$?
  if [ "$1" = ok ] && [ $rc -ne 0 ]; then echo "FAIL: $2 应通过：$out"; fails=$((fails+1)); fi
  if [ "$1" = fail ] && [ $rc -eq 0 ]; then echo "FAIL: $2 应被拒"; fails=$((fails+1)); fi
  if [ -n "${3:-}" ] && ! grep -qF -- "$3" <<<"$out"; then echo "FAIL: $2 输出缺少“$3”：$out"; fails=$((fails+1)); fi
}

setup; expect ok "原样"
setup; dup_into Twin; expect fail "两个猜想下同一编号" "duplicate id 20261014-01"
setup; mkdir -p "$T/r/Archive/Old"; cp "$T/r/Conjectures/Goldbach/S20261014_01.json" "$T/r/Archive/Old/"
expect fail "复用已归档编号" "已归档条目"
setup; mkdir -p "$T/r/Archive/Old"; cp "$T/r/Conjectures/Goldbach/S20261014_02.json" "$T/r/Archive/Old/S20261014_09.json"
python3 -I -c "import json,sys;p=sys.argv[1];m=json.load(open(p));m['id']='20261014-09';json.dump(m,open(p,'w'))" "$T/r/Archive/Old/S20261014_09.json"
expect ok "归档里另有不冲突的编号"

echo "validate_meta tests: $([ $fails -eq 0 ] && echo PASS || echo "$fails FAIL")"
exit $([ $fails -eq 0 ] && echo 0 || echo 1)
