#!/usr/bin/env bash
# 证明验证·第二步：在全新的工作区里检查。登记库自己的表述和验证器从源码重新编译，
# 只从上一步取证明自己的 .olean，然后检查：
#   1. 定理的类型正好是这条表述（证否时正好是 ¬ 表述）；证明里不能另外定义同名“表述”（导入会冲突）
#   2. 只用三个标准公理，没有 sorry；native_decide 的每一步由内核重新计算，通过才接受，并标出来
#   3. 用 Lean 内核重放证明模块的全部声明（leanchecker）
# 输入：edit-out/result.json、proof-out/oleans.tar。输出：proof-out/verify.json、message.md。代码许可：Apache-2.0。
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
OUT=proof-out; mkdir -p "$OUT"
fail() { { echo "### 没有通过验证"; echo; echo "$1"; } > "$OUT/message.md"; echo "ok=false" >> "$GITHUB_OUTPUT"; exit 0; }
read -r ROOT MODULE THEOREM STMT STMT_MOD DIRECTION < <(python3 -c '
import json; p = json.load(open("edit-out/result.json"))["proof"]
print(p["root"], p["module"], p["theorem"], p["statement"], p["statement_module"], p.get("direction", "prove"))')
curl -sSfL https://github.com/leanprover/elan/releases/latest/download/elan-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /tmp
/tmp/elan-init -y --no-modify-path --default-toolchain "$(cat lean-toolchain)" > /dev/null
export PATH="$HOME/.elan/bin:$PATH"
lake exe cache get > "$OUT/cache.log" 2>&1 || fail "下载 Mathlib 缓存失败，这不是你的问题，请稍后重新提交。"
lake build "$STMT_MOD" verify > "$OUT/trusted.log" 2>&1 || fail "编译登记库自己的表述失败，这不是你的问题，维护者会查看。"
# 解包前检查每一项：只能是证明顶层名下的普通文件
python3 -I - "$OUT/oleans.tar" "$ROOT" <<'PY' || fail "编译结果里有不该有的文件。"
import sys, tarfile
tar, root = sys.argv[1], sys.argv[2]
with tarfile.open(tar) as t:
    ms = t.getmembers()
    for m in ms:
        n = m.name.removeprefix("./")
        if not m.isfile() or ".." in n.split("/") or not (n.startswith(f"lib/lean/{root}.") or n.startswith(f"lib/lean/{root}/")):
            sys.exit(f"bad member {m.name}")
    t.extractall(".lake/build", members=ms, filter="data")
PY
timeout 120m lake env .lake/build/bin/verify "$OUT/verify.json" "$MODULE" "$THEOREM" "$STMT" "$STMT_MOD" "$DIRECTION" > "$OUT/verify.log" 2>&1 \
  || fail "$(python3 -c '
import json
try: r = json.load(open("proof-out/verify.json")); print("\n".join("- " + x for x in r["reasons"]))
except Exception: print(open("proof-out/verify.log").read()[-3000:])')"
LC="$(lean --print-prefix)/bin/leanchecker"
if [ -x "$LC" ]; then
  lake env "$LC" "$MODULE" > "$OUT/leanchecker.log" 2>&1 || fail "Lean 内核重放（leanchecker）没有通过：
\`\`\`
$(tail -20 "$OUT/leanchecker.log")
\`\`\`"
else
  fail "找不到 leanchecker，这不是你的问题，维护者会查看。"
fi
AX=$(python3 -c 'import json;print(",".join(json.load(open("proof-out/verify.json"))["axioms"]))')
NATIVE=$(python3 -c 'import json;print(",".join(json.load(open("proof-out/verify.json")).get("native_decide", [])))')
if [ "$DIRECTION" = "disprove" ]; then WHAT="证否"; TYPE="¬ $STMT"; else WHAT="证明"; TYPE="$STMT"; fi
{ echo "### ${WHAT}验证通过"; echo
  echo "定理 \`$THEOREM\` 的类型正好是 \`$TYPE\`。用 Lean $(cut -d: -f2 lean-toolchain) 和 Mathlib v4.29.0 编译通过，只用了标准公理（${AX:-无}），并经 Lean 内核重放。"
  if [ -n "$NATIVE" ]; then echo; echo "**！注意：证明用了 native_decide。** 登记库已让 Lean 内核把这些计算重新算了一遍，结果一致：\`${NATIVE//,/\`、\`}\`。页面上会标出感叹号。"; fi
} > "$OUT/message.md"
{ echo "ok=true"; echo "axioms=$AX"; echo "native=$NATIVE"; } >> "$GITHUB_OUTPUT"
