---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-0.2.1+afd2.sol61.20261009.1"
applies_to: [adaptive-task-router]
supersedes: []
---

# Adaptive Task Router · AFD 2.0 完整版

可独立阅读、审查和安装的 Codex 多代理协作插件。不需要其他版本或差异补丁；业务项目资料只在处理相应项目任务时按需读取。

当前版本：`0.2.1+afd2.sol61.20261009.1`。状态：AFD 接入优化候选；本次不修改 AFD 业务仓库，不代表已经安装、接入生产或通过真实多代理验收。实际检查与未测范围见[核验记录](docs/VALIDATION.md)。

## 从哪里开始

- 审查：[审查说明](PRO_REVIEW.md)，两个技能和五份执行参考。
- 使用：[使用指南](docs/USAGE.md)；处理 AFD 开发／维护时按需读取 [AFD 适配](skills/route-task/references/afd-integration.md)。
- 安装：[安装指南](docs/INSTALLATION.md)，先验证实际加载，再验证任务行为。
- 验证：[行为场景](tests/SCENARIOS.md)；检查器回归使用 `python3 -B -m unittest discover -s tests -p 'test_*.py' -v`。

## 能做什么

一次明确启用后，在当前对话持续分析任务目标、难度、依赖和验收，按需选择模型与推理档位并协调原生子代理。简单任务直接完成；复杂任务支持实施、调查、整合、独立复核及有收益的递归。

整树共享容量，管理资源修改权、输入版本、失败诊断、停止传播及恢复。保留 `gpt-6-astra`、`gpt-6.1-sol`、`gpt-6-luna` 的 17 项选型起点；它们是策略参考，不是当前账户可用性或性能保证。实际参数以本次宿主 schema 为准。

AFD 适配区分代理名额、工程实施、重检查和浏览器资源；衔接已有任务状态、授权和累计预算，不新增后台服务或任务库。动态选型、实施帮手和递归没有被永久缩减为固定只读配置；使用范围由当前有效授权和实际能力共同决定。

## 两个入口

| 技能 | 使用方式 | 职责 |
| --- | --- | --- |
| [route-task](skills/route-task/SKILL.md) | 明确调用后在当前对话持续使用 | 分析、选型、原生委派、协调与验收 |
| [suggest-task-routing](skills/suggest-task-routing/SKILL.md) | 允许自动发现，只建议 | 判断分工收益，等待用户接受 |

```text
请使用 $adaptive-task-router:route-task 完成以下任务：……
按当前项目授权与验收执行，在本对话后续请求中持续按需选型、分工和验收。
```

“这次不用”只影响当前范围；“关闭”持续停用；“先停止”暂停工作，收到继续指令后才恢复。仅讨论插件、引用启用语句或安装文件不算行动授权。

## 边界与验证

插件使用宿主原生能力，不包含运行服务、API key、MCP、Apps 或 hooks，不热切换主线程或修改全局模型、权限和容量。协作规则不是强制安全隔离，不额外授予真实 I/O、生产、发布或正式调度权限。缺原生能力时完成当前代理能做的授权工作，不改走外部付费服务或额外 CLI。

结构检查与确定性回归不证明模型遵守规则。目录发现、实际安装、Skill 加载、真实派工、停止恢复和业务成功分别取证；未回显配置如实标记未知。本版没有真实多模型效果、成本或耗时对照。

文件包括 `.codex-plugin/plugin.json`、指向本包的 `.agents/plugins/marketplace.json`、`skills/`、`docs/` 及 `tests/`。来源与版权见[来源声明](NOTICE.md)和 [MIT 许可证](LICENSE)；不是 OpenAI 官方插件。
