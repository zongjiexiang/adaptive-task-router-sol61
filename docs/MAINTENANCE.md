---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-0.2.3+afd2.sol61.20261009.1"
applies_to: [adaptive-task-router]
supersedes: []
---

# 维护与验证

源码目录是维护位置，安装缓存可重建；完整包是固定版本的分发材料，不依赖私人目录或旧补丁。

## 唯一维护位置

| 内容 | 位置（相对 skills/） |
| --- | --- |
| 启用、单次例外、关闭和交付 | route-task/SKILL.md |
| 17 项选型起点 | route-task/references/model-routing.md |
| 局部求解、整合与验证 | route-task/references/high-effort-orchestration.md |
| 原生 schema、角色与配置证据 | route-task/references/native-dispatch.md |
| 容量、版本、失败与停止恢复 | route-task/references/recursive-orchestration.md |
| AFD 授权、实施权、预算与验收衔接 | route-task/references/afd-integration.md |
| 尚未启用时的建议 | suggest-task-routing/SKILL.md |

不复制第二套模型表或 AFD 业务合同。修改当前行为的文件更新自身元数据；未改的原作与历史记录保留来源日期。清单版本及当前交付文档同步，既往测试记录不得冒充本版实测。

## 确定性检查

在完整插件根运行：

```sh
python3 -B tests/check_structure.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

使用 Python 3.11+、Git、Bash，开发依赖按 `requirements-dev.txt` 安装。结构检查覆盖清单、市场、技能入口、包内引用及完整模型表；支持表格首尾竖线省略，先解析全部选项再拒绝未知、重复和缺失项。

型号检查同时读取原文与解析后的字符串，包括 Markdown front matter，以及整个包内的 `.json`、`.yaml`、`.yml`、`.toml`（后缀大小写均可）。新增角色、未引用配置及技能链接到的上述配置都进入检查；嵌套列表、映射和 YAML 循环别名有界遍历。损坏配置以及尚未支持的 `.json5`、`.jsonc`、`.ini`、`.cfg`、`.conf` 明确失败；引入新配置格式前须增加解析规则和反例。该范围不包含任意脚本、模板或运行时动态生成的配置。

检查跳过 `.git`，拒绝越过包边界的符号链接，不读取宿主全局配置或外部角色。回归测试使用合成临时目录，不调用模型、认证或业务；外部角色和实际加载仍须原生验证。

CI 执行相同命令，并以事件中的明确对象检查已提交差异：PR 使用 base/head SHA，push 使用 before/head SHA；首次 push 或手动运行没有基线时，以空树比较整个候选。取得完整历史，旧基线对象缺失时尝试获取，仍不可用则失败；另保留工作树差异检查。事件字段见 [GitHub 官方上下文说明](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)。包级检查、单 Skill 验证器、原生加载和实际模型行为是不同结论。详见[核验记录](VALIDATION.md)。

## 行为验收与校准

按[行为场景](../tests/SCENARIOS.md)选择受影响项。入口保留应触发、不触发和失败边界；实施、递归、停止恢复须有真实原生身份、版本和状态证据。测试预期与执行提示分开，不把“请证明规则成立”交给模型自评分。

真实任务校准固定输入和验收，分别比较质量、返工、总等待及工具可得用量；不跑全组合，不从共享额度推算成本。结构与夹具通过不证明权限隔离或自然业务恢复。

## 打包

保留许可证、隐藏清单、市场、全部技能与参考、测试和当前核验记录。排除 `.git`、私人配置、凭据、原始日志与临时产物；核对完整清单及逐文件 SHA-256，从解压件重跑检查。每次变更使用新补丁版本，旧版本内容不覆盖。项目安装与启用按[安装指南](INSTALLATION.md)另行执行。
