#!/usr/bin/env python3
"""把一条“声明证明”议题（.github/ISSUE_TEMPLATE/claim.yml 表单）写进对应表述的
claimed_proofs。由 .github/workflows/claim.yml 调用。

用法：claim_from_issue.py <issue_number> <issue_url> < issue_body.md
成功时在 stdout 打印被修改的 JSON 路径；找不到表述或字段缺失则非零退出并打印原因。
代码许可：Apache-2.0。
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def parse_form(body):
    """GitHub 表单议题正文形如：### 标签\\n\\n值\\n\\n### 标签 ..."""
    fields = {}
    for m in re.finditer(r"^### (.+?)\s*\n+(.*?)(?=^### |\Z)", body, re.S | re.M):
        fields[m.group(1).strip()] = m.group(2).strip()
    return fields

def main():
    issue_no, issue_url = sys.argv[1], sys.argv[2]
    f = parse_form(sys.stdin.read())
    sid = f.get("表述编号", "").lstrip("#").strip()
    claimant, date, url = f.get("声称方", "").strip(), f.get("声称日期", "").strip(), f.get("证明链接", "").strip()
    note = f.get("备注（可选，只写事实）", "").strip()
    if note in ("_No response_", "无"): note = ""
    missing = [k for k, v in [("表述编号", sid), ("声称方", claimant), ("声称日期", date), ("证明链接", url)] if not v]
    if missing:
        print("缺少字段：" + "、".join(missing)); return 1
    if not re.match(r"^\d{8}-\d{2}$", sid):
        print(f"编号格式不对：{sid!r}，应为 YYYYMMDD-NN"); return 1
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        print(f"日期格式不对：{date!r}，应为 YYYY-MM-DD"); return 1
    if not url.startswith("http"):
        print("证明链接必须是 http(s) 地址"); return 1
    d, n = sid.split("-")
    matches = list((ROOT / "Conjectures").glob(f"*/S{d}_{n}.json"))
    if not matches:
        print(f"找不到表述 #{sid}（已归档的表述不接受新声明）"); return 1
    p = matches[0]
    meta = json.loads(p.read_text(encoding="utf-8"))
    claims = meta.setdefault("claimed_proofs", [])
    if any(c.get("url") == url for c in claims):
        print(f"该链接已登记在 #{sid} 下"); return 1
    claims.append({"claimant": claimant, "date": date, "url": url, "note": note, "issue": issue_url})
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(p.relative_to(ROOT)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
