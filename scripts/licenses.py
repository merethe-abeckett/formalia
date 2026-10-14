"""登记库接受的条目许可（SPDX 标识）。代码许可：Apache-2.0。

复合许可：每条表述按它自己声明的许可发布，未声明时默认 CC-BY-4.0。
改编或照录的表述必须声明许可，并且应与原作许可一致或兼容。
编辑一条已有表述的信息，即同意按该条目的许可发布你的修改，和维基百科相同。
"""
DEFAULT = "CC-BY-4.0"
ALLOWED = {
    "CC-BY-4.0":    ("知识共享 署名 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "CC-BY-SA-4.0": ("知识共享 署名-相同方式共享 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "CC0-1.0":      ("CC0 公有领域贡献", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "Apache-2.0":   ("Apache 许可证 2.0", "https://www.apache.org/licenses/LICENSE-2.0"),
    "MIT":          ("MIT 许可证", "https://opensource.org/license/mit"),
}

def of(meta):
    return meta.get("license") or DEFAULT
