#!/usr/bin/env bash
# apply_edit.py 的回归测试：在临时副本里跑，不改动仓库。bash tests/test_apply_edit.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp -r "$REPO/scripts" "$REPO/Conjectures" "$TMP/"
cd "$TMP"
pass=0; fail=0
issue() { python3 -c 'import json,sys; print("摘要\n\n<!-- formalia-edit v1 -->\n```json\n"+json.dumps(json.loads(sys.stdin.read()),ensure_ascii=False)+"\n```")'; }
expect() {  # $1 期望退出码  $2 说明  $3 提交 JSON  $4 期望出现在消息里的文字
  set +e; out=$(echo "$3" | issue | python3 scripts/apply_edit.py --issue 1 --created-at 2026-10-15T03:00:00Z --result r.json); code=$?; set -e
  if [ "$code" = "$1" ] && [[ "$out" == *"$4"* ]]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $2 (exit $code): $out"; fi
}
ED='"editor":{"label":"匿名者 00000000"}'
expect 0 "claim"            '{"v":1,"type":"claim","target":"20261014-02",'"$ED"',"data":{"claimant":"x","date":"2026-10-10","url":"https://e.org/p"}}' "已通过"
expect 1 "duplicate claim"  '{"v":1,"type":"claim","target":"20261014-02",'"$ED"',"data":{"claimant":"x","date":"2026-10-10","url":"https://e.org/p"}}' "已经登记"
expect 1 "js url"           '{"v":1,"type":"claim","target":"20261014-02",'"$ED"',"data":{"claimant":"x","date":"2026-10-10","url":"javascript:alert(1)"}}' "http"
expect 1 "future date"      '{"v":1,"type":"claim","target":"20261014-02",'"$ED"',"data":{"claimant":"x","date":"2999-01-01","url":"https://e.org/q"}}' "将来"
expect 1 "missing target"   '{"v":1,"type":"claim","target":"20991231-01",'"$ED"',"data":{"claimant":"x","date":"2026-10-10","url":"https://e.org/q"}}' "找不到"
expect 1 "meta conflict"    '{"v":1,"type":"meta","target":"20261014-01",'"$ED"',"data":{"restatement":"新"},"base":{"restatement":"旧"}}' "编辑冲突"
expect 1 "meta forbidden"   '{"v":1,"type":"meta","target":"20261014-01",'"$ED"',"data":{"submitted_by":"me"}}' "不能编辑"
expect 1 "meta no change"   '{"v":1,"type":"meta","target":"20261014-01",'"$ED"',"data":{"external_links":[]}}' "完全相同"
expect 0 "meta ok"          '{"v":1,"type":"meta","target":"20261014-01",'"$ED"',"data":{"external_links":[{"label":"a","url":"https://e.org/a"}]},"base":{"external_links":[]}}' "已通过"
expect 0 "statement"        '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True"}}' "#20261015-01"
expect 0 "statement 2 → next id" '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"False"}}' "#20261015-02"
expect 1 "eval injection"   '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True\n#eval 1"}}' "不允许"
expect 1 "bad import"       '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Lean"],"proposition":"True"}}' "import"
expect 1 "adapted no url"   '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True","license":"CC-BY-4.0","source":{"kind":"adapted"}}}' "来源链接"
expect 1 "dup conjecture"   '{"v":1,"type":"statement",'"$ED"',"data":{"new_conjecture":{"name":"Goldbach","informal":"x"},"imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True"}}' "同名"
expect 1 "adapted no licence" '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True","source":{"kind":"adapted","url":"https://e.org/src"}}}' "必须选择许可"
expect 1 "unknown licence"  '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True","license":"GPL-3.0"}}' "许可只能是"
expect 0 "adapted Apache"   '{"v":1,"type":"statement",'"$ED"',"data":{"conjecture":"goldbach","imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"True ∧ True","license":"Apache-2.0","source":{"kind":"adapted","url":"https://e.org/src"}}}' "已通过"
grep -q '"license": "Apache-2.0"' Conjectures/Goldbach/S20261015_03.json && grep -q "内容许可：Apache-2.0" Conjectures/Goldbach/S20261015_03.lean && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: licence not written to json/lean"; }
grep -q '"license": "CC-BY-4.0"' Conjectures/Goldbach/S20261015_01.json && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: default licence not applied"; }
before=$(find Conjectures -type f | wc -l)
expect 1 "atomic on failure" '{"v":1,"type":"statement",'"$ED"',"data":{"new_conjecture":{"name":"Brand New","informal":"x"},"imports":["Mathlib.Data.Nat.Prime.Defs"],"proposition":"sorry"}}' "sorry"
after=$(find Conjectures -type f | wc -l)
if [ "$before" = "$after" ] && [ ! -d Conjectures/BrandNew ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: failed edit left files behind"; fi
python3 scripts/validate_meta.py > /dev/null && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: validate_meta after edits"; }
echo "apply_edit tests: $pass passed, $fail failed"
[ "$fail" = 0 ]
