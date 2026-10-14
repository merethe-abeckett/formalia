#!/usr/bin/env bash
# Edit 工作流的检查步骤。在没有任何密钥、只有只读权限的任务里运行。
# 输入（环境变量）：BODY ISSUE CREATED AUTHOR MODE(web|claim-form)
# 输出：edit-out/result.json、edit-out/message.md；向 $GITHUB_OUTPUT 写 ok / needs_lean / needs_proof / target
# 退出码总是 0：失败通过 ok=false 传给后续任务。代码许可：Apache-2.0。
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
OUT=edit-out; mkdir -p "$OUT"
needs_lean=false; needs_proof=false; target=""
args=(--issue "$ISSUE" --created-at "$CREATED" --result "$OUT/result.json")
[ "${MODE:-web}" = "claim-form" ] && args+=(--claim-form --author "$AUTHOR")
printf '%s' "$BODY" | python3 scripts/apply_edit.py "${args[@]}" > "$OUT/apply.log" 2>&1
fail() {   # $1 = 给提交者看的说明
  { echo "### 没有通过检查"; echo; echo "$1"; } > "$OUT/message.md"
  { echo "ok=false"; echo "needs_lean=$needs_lean"; echo "needs_proof=false"; echo "target=$target"; } >> "$GITHUB_OUTPUT"
  exit 0
}
[ -f "$OUT/result.json" ] || fail "处理程序出错，这不是你的问题。维护者会查看运行记录。"
read -r ok needs_lean needs_proof target < <(python3 - "$OUT/result.json" <<'PY'
import json, re, sys
r = json.load(open(sys.argv[1]))
t = r.get("target") or ""
print(str(r.get("ok")).lower(), str(r.get("needs_lean")).lower(), str(r.get("needs_proof")).lower(), t if re.fullmatch(r"[0-9A-Za-z-]{1,60}", t) else "-")
PY
)
[ "$target" = "-" ] && target=""
[ "$ok" = "true" ] || fail "$(python3 -c "import json;print(json.load(open('$OUT/result.json'))['message'])")"

python3 scripts/validate_meta.py > "$OUT/validate.log" 2>&1 || fail "元数据校验失败：
\`\`\`
$(tail -20 "$OUT/validate.log")
\`\`\`"

if [ "$needs_lean" = "true" ]; then
  # 不可信的 Lean 代码只在这里编译。本任务没有密钥，令牌只读。
  # 结果文件在编译前已经写定，编译过程即使篡改工作区，后续写入任务也会重新生成并比对。
  curl -sSfL https://github.com/leanprover/elan/releases/latest/download/elan-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /tmp
  /tmp/elan-init -y --no-modify-path --default-toolchain "$(cat lean-toolchain)" > /dev/null
  export PATH="$HOME/.elan/bin:$PATH"
  lake exe cache get > "$OUT/cache.log" 2>&1 || fail "下载 Mathlib 缓存失败，这不是你的问题，请稍后重新提交。"
  scripts/run_checks.sh > "$OUT/lean.log" 2>&1 || fail "Lean 检查没有通过（编译错误、sorry、native_decide 或非标准公理）。日志末尾：
\`\`\`
$(grep -v '^trace' "$OUT/lean.log" | tail -40)
\`\`\`"
  scripts/lean4checker.sh > "$OUT/l4c.log" 2>&1 || fail "lean4checker 独立复核没有通过：
\`\`\`
$(tail -20 "$OUT/l4c.log")
\`\`\`"
fi

{ echo "### 检查通过"; echo; python3 -c "import json;print(json.load(open('$OUT/result.json'))['message'])"; } > "$OUT/message.md"
{ echo "ok=true"; echo "needs_lean=$needs_lean"; echo "needs_proof=$needs_proof"; echo "target=$target"; } >> "$GITHUB_OUTPUT"
