# 巡查判定规则与环境变量处理的测试：python3 tests/test_patrol.py
import importlib.util, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("patrol", ROOT / "patrol" / "patrol.py")
patrol = importlib.util.module_from_spec(spec); spec.loader.exec_module(patrol)

fails = 0
def check(cond, msg):
    global fails
    if not cond: fails += 1; print("FAIL:", msg)

# 判定表（docs/DELETION.md）：缺少检查器报告不是 CI 证据
cases = [
    ([True, True], "fail", "deletion-proposal"),
    ([True, True], "ok", "patrol-finding"),
    ([True, True], "missing", "patrol-finding"),
    ([True, False], "fail", "patrol-disagreement"),
    ([False, True], "missing", "patrol-disagreement"),
    ([False, False], "fail", None),
    ([True], "fail", "patrol-finding"),     # 单模型永远不开提删
    ([False], "fail", None),
]
for flags, ci, want in cases:
    got = patrol.decide_kind(flags, ci)
    check(got == want, f"decide_kind({flags}, {ci!r}) = {got!r}, want {want!r}")

# 检查器事实
check(patrol.ci_status(None, None) == "missing", "no report -> missing")
check(patrol.ci_status({"declarations": []}, None) == "fail", "report without the declaration -> fail")
check(patrol.ci_status({}, {"ok": True, "is_prop": True}) == "ok", "ok report -> ok")
check(patrol.ci_status({}, {"ok": True, "is_prop": False}) == "fail", "not a Prop -> fail")
check(patrol.ci_status({}, {"ok": False, "is_prop": True}) == "fail", "checker failed -> fail")

# 空字符串的仓库变量等于未设置
os.environ["X_PATROL_TEST"] = ""
check(patrol.env("X_PATROL_TEST", "dflt") == "dflt", "empty env var falls back to default")
os.environ["X_PATROL_TEST"] = "  qwen-max "
check(patrol.env("X_PATROL_TEST", "dflt") == "qwen-max", "env var is stripped")
del os.environ["X_PATROL_TEST"]
check(patrol.env("X_PATROL_TEST", "dflt") == "dflt", "unset env var falls back to default")

# 空的 QWEN_BASE_URL / QWEN_MODEL 不能拼出坏地址
seen = {}
patrol.http_json = lambda url, payload, headers, timeout=120: seen.update(url=url, model=payload["model"]) or \
    {"choices": [{"message": {"content": "{}"}}]}
os.environ.update(QWEN_API_KEY="k", QWEN_BASE_URL="", QWEN_MODEL="")
patrol.ask_qwen("p")
check(seen["url"] == "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions", f"qwen url {seen['url']!r}")
check(seen["model"] == "qwen-plus", f"qwen model {seen['model']!r}")

# 测试替身只看代码，不看注释
wrap = lambda code: "File x:\n```lean\n" + code + "\n```\n"
import json
fake = lambda code: json.loads(patrol.ask_fake(wrap(code)))["problem"]
check(not fake("/- 去掉了 answer(sorry) ↔ -/\ndef S : Prop := True"), "sorry in block comment ignored")
check(not fake("-- sorry\ndef S : Prop := 1 = 1"), "sorry in line comment ignored")
check(not fake("/- 外 /- 内 sorry -/ 仍在注释里 sorry -/ def S : Prop := 1 = 1"), "nested comment ignored")
check(fake("def S : Prop := sorry"), "sorry in code flagged")
check(fake("def S : Prop := True ∧ 1 = 1"), "True ∧ in code flagged")

print("patrol tests:", "PASS" if not fails else f"{fails} FAIL")
sys.exit(1 if fails else 0)
