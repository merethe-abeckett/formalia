#!/usr/bin/env bash
# 证明验证·第一步：编译提交的证明。没有任何密钥、令牌只读。
# 证明是完整的 Lean，编译时可以执行任意代码，所以这里的一切产物都不被信任：
# 下一步只取证明自己的 .olean，在全新的工作区里检查。
# 输入：edit-out/result.json（apply_edit.py 的输出）。输出：proof-out/。代码许可：Apache-2.0。
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
OUT=proof-out; mkdir -p "$OUT"
fail() { { echo "### 证明没有通过"; echo; echo "$1"; } > "$OUT/message.md"; echo "ok=false" >> "$GITHUB_OUTPUT"; exit 0; }
python3 -I scripts/proof_stage.py edit-out/result.json > "$OUT/stage.log" 2>&1 || fail "$(cat "$OUT/stage_error.txt" 2>/dev/null || tail -5 "$OUT/stage.log")"
ROOT=$(python3 -c 'import json;print(json.load(open("edit-out/result.json"))["proof"]["root"])')
curl -sSfL https://github.com/leanprover/elan/releases/latest/download/elan-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /tmp
/tmp/elan-init -y --no-modify-path --default-toolchain "$(cat lean-toolchain)" > /dev/null
export PATH="$HOME/.elan/bin:$PATH"
lake exe cache get > "$OUT/cache.log" 2>&1 || fail "下载 Mathlib 缓存失败，这不是你的问题，请稍后重新提交。"
timeout 290m lake build "$ROOT" > "$OUT/build.log" 2>&1
code=$?
[ $code = 124 ] && fail "编译超过 290 分钟，未能验证。"
[ $code = 0 ] || fail "证明没有编译通过（Lean 4.29.0 / Mathlib v4.29.0）。日志末尾：
\`\`\`
$(grep -v '^trace' "$OUT/build.log" | tail -40)
\`\`\`"
# 只打包证明自己的编译结果
(cd .lake/build && find . -type f \( -path "./lib/lean/$ROOT.*" -o -path "./lib/lean/$ROOT/*" \) -print0 | tar -cf "../../$OUT/oleans.tar" --null -T -)
[ -s "$OUT/oleans.tar" ] || fail "编译通过了，但没有找到编译结果文件。这不是你的问题，维护者会查看。"
echo "ok=true" >> "$GITHUB_OUTPUT"
