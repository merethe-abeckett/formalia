#!/usr/bin/env python3
"""Gemini 调用的公用模块（只用标准库）。

- 模型名来自 GEMINI_MODEL；未设置时默认 gemini-3.8-flash。
- 配置的模型返回 404 时，自动调用 ListModels，挑一个名字含 "flash"、支持
  generateContent 的最新模型，并把可用列表打到 stderr，方便更新 GEMINI_MODEL。
- 其他 HTTP 错误原样抛出 GeminiError，调用方不得把它当成“无问题”。
代码许可：Apache-2.0。
"""
import json, os, sys, urllib.request, urllib.error

BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.8-flash"

class GeminiError(Exception):
    pass

def _key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k: raise GeminiError("未设置 GEMINI_API_KEY")
    return k

def _request(url, payload=None, timeout=180):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "x-goog-api-key": _key()})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        raise GeminiError(f"HTTP {e.code} {url.split('/models/')[-1].split(':')[0]}: {body}") from None
    except urllib.error.URLError as e:
        raise GeminiError(f"网络错误: {e.reason}") from None

def list_models():
    out = _request(f"{BASE}/models?pageSize=100")
    models = []
    for m in out.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            models.append(m["name"].split("/", 1)[-1])
    return models

_resolved = None
def resolve_model():
    """返回可用的模型名；必要时自动发现并缓存。"""
    global _resolved
    if _resolved: return _resolved
    want = os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL
    try:
        _request(f"{BASE}/models/{want}")
        _resolved = want
        return want
    except GeminiError as e:
        if "HTTP 404" not in str(e): raise
    models = list_models()
    print(f"[gemini] 模型 {want!r} 不存在。当前可用：{', '.join(models) or '（空）'}", file=sys.stderr)
    cands = [m for m in models if "flash" in m and "lite" not in m and "image" not in m and "tts" not in m and "live" not in m]
    cands = sorted(cands, reverse=True) or sorted([m for m in models if m.startswith("gemini")], reverse=True)
    if not cands: raise GeminiError("找不到任何支持 generateContent 的 Gemini 模型")
    _resolved = cands[0]
    print(f"[gemini] 改用 {_resolved!r}。建议把仓库变量 GEMINI_MODEL 设为这个值。", file=sys.stderr)
    return _resolved

import re as _re

def _suggested_model(err_text):
    """从 404 报错里读出 Google 建议改用的模型名。"""
    m = _re.search(r"use models/([A-Za-z0-9.\-]+)", err_text)
    return m.group(1) if m else None

def generate(prompt, temperature=0.2, json_mode=False):
    global _resolved
    model = resolve_model()
    cfg = {"temperature": temperature}
    if json_mode: cfg["responseMimeType"] = "application/json"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": cfg}
    try:
        out = _request(f"{BASE}/models/{model}:generateContent", payload)
    except GeminiError as e:
        if "HTTP 404" not in str(e): raise
        # 模型信息能查到但生成被拒（如“对新用户不再开放”）：按 Google 的建议换模型重试一次
        alt = _suggested_model(str(e))
        if not alt:
            _resolved = None
            models = list_models()
            cands = sorted([m for m in models if "flash" in m and not any(x in m for x in ("lite","image","tts","live"))], reverse=True)
            if not cands: raise
            alt = cands[0]
        print(f"[gemini] 模型 {model!r} 不可用，改用 {alt!r}。建议把仓库变量 GEMINI_MODEL 设为这个值。", file=sys.stderr)
        _resolved = alt
        out = _request(f"{BASE}/models/{alt}:generateContent", payload)
    try:
        return out["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise GeminiError(f"响应中没有文本: {json.dumps(out)[:300]}")

if __name__ == "__main__":
    print("可用模型：", *list_models(), sep="\n  ")
    print("将使用：", resolve_model())
