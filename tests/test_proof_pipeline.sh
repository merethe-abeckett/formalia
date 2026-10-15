#!/usr/bin/env bash
# 证明验证流程的端到端测试（CI 里运行，需要 elan 和 Mathlib 缓存）。
# 临时登记一条可证的表述 1 + 1 = 2，再用一份正确的证明和几份作弊的证明分别走一遍
# proof_build.sh → proof_check.sh：正确的必须通过，作弊的必须被拒。代码许可：Apache-2.0。
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p Conjectures/ZzTest
cat > Conjectures/ZzTest/S20000101_01.lean <<'LEAN'
module

public import Mathlib.Data.Nat.Prime.Defs

@[expose] public section

namespace Registry.ZzTest

/-- 测试用表述。 -/
def S20000101_01 : Prop :=
  1 + 1 = 2

end Registry.ZzTest

end
LEAN
cat > Conjectures/ZzTest/S20000101_01.json <<'JSON'
{"id": "20000101-01", "conjecture": "zztest", "module": "Conjectures.ZzTest.S20000101_01",
 "declaration": "Registry.ZzTest.S20000101_01", "submitted_by": "test", "submitted_at": "2000-01-01",
 "source": {"kind": "original"}, "claimed_proofs": []}
JSON
sed -e 's/S20000101_01/S20000101_02/g' -e 's/1 + 1 = 2/1 + 1 = 3/' Conjectures/ZzTest/S20000101_01.lean > Conjectures/ZzTest/S20000101_02.lean
sed -e 's/S20000101_01/S20000101_02/g' -e 's/20000101-01/20000101-02/' Conjectures/ZzTest/S20000101_01.json > Conjectures/ZzTest/S20000101_02.json
echo '{"slug": "zztest", "name": "Test", "informal": "1 + 1 = 2"}' > Conjectures/ZzTest/conjecture.json
cp lakefile.toml /tmp/lakefile.orig
pass=0; fail=0
run() {   # $1 期望(pass|fail)  $2 说明  $3 证明文件  $4 期望出现在消息里的文字  [$5 表述编号  $6 方向]
  rm -rf proof-out edit-out Submitted .lake/build/lib/lean/Proof .lake/build/lib/lean/Proof.*
  cp /tmp/lakefile.orig lakefile.toml
  mkdir -p edit-out
  python3 - "$3" "${5:-20000101-01}" "${6:-prove}" <<'PY' | python3 scripts/apply_edit.py --issue 7 --created-at 2026-10-15T00:00:00Z --result edit-out/result.json > /dev/null || true
import json, sys
sub = {"v": 1, "type": "claim", "target": sys.argv[2], "editor": {"label": "测试"},
       "data": {"direction": sys.argv[3], "claimant": "test", "date": "2026-10-14", "theorem": "Proof.ok", "proof": open(sys.argv[1]).read()}}
print("<!-- formalia-edit v1 -->\n```json\n" + json.dumps(sub, ensure_ascii=False) + "\n```")
PY
  git checkout -q -- Conjectures/ 2>/dev/null || true   # apply_edit 写入的声明不影响后续测试
  rm -rf Proofs
  out=$(mktemp); export GITHUB_OUTPUT=$out
  scripts/proof_build.sh
  if grep -q '^ok=true' "$out"; then : > "$out"; scripts/proof_check.sh; fi
  got=fail; grep -q '^ok=true' "$out" && got=pass
  msg=$(cat proof-out/message.md 2>/dev/null || true)
  if [ "$got" = "$1" ] && [[ "$msg" == *"$4"* ]]; then pass=$((pass+1)); echo "ok   $2"
  else fail=$((fail+1)); echo "FAIL $2: expected $1, got $got"; echo "$msg" | head -30; fi
}
run pass "正确的证明"            tests/proofs/good.lean       "证明验证通过"
run fail "sorry"                 tests/proofs/sorry.lean      "sorry"
run fail "类型不是表述本身"      tests/proofs/wrongtype.lean  "类型不是"
run fail "自定义公理"            tests/proofs/axiom.lean      "非标准公理"
run pass "native_decide（内核重算后标出）" tests/proofs/native.lean "native_decide"
run fail "伪造的 native_decide 公理" tests/proofs/fakenative.lean "内核没能" 20000101-02
run pass "证否"                  tests/proofs/disprove.lean   "证否验证通过" 20000101-02 disprove
run fail "证明当作证否提交"      tests/proofs/good.lean       "类型不是 ¬" 20000101-01 disprove
run fail "自己重新定义表述"      tests/proofs/redefine.lean   "导入失败"
run fail "导入登记库工具"        tests/proofs/badimport.lean  "不允许的导入"
cp /tmp/lakefile.orig lakefile.toml
rm -rf Conjectures/ZzTest proof-out edit-out Submitted
echo "proof pipeline tests: $pass passed, $fail failed"
[ "$fail" = 0 ]
