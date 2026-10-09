---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-0.2.2+afd2.sol61.20261009.1"
applies_to: [adaptive-task-router]
supersedes: []
---

# 安装与启用

完整插件包与项目接入是两个交付。先在获准的隔离工作目录验证，不因本包已优化就自动修改 AFD、个人配置或旧业务系统。

## 保留完整源码与固定版本

保留隐藏的 `.codex-plugin` 和 `.agents`。通过 `codex --version`、`codex plugin --help` 确认实际客户端能力；结构检查需要 Python 3.10+ 和 `requirements-dev.txt` 中的 PyYAML，插件执行不需要 Python 服务。

本包市场名为 `afd2-sol61`，插件 ID 为 `adaptive-task-router@afd2-sol61`；自带市场的本地 source.path 为 `.`，以完整包根为基准。固定实际候选提交和清单版本，避免从另一个远程来源安装同名插件。

## 发现不等于安装，配置不等于加载

使用宿主支持的目录／安装流程。官方当前指南把 CLI 市场登记与桌面端实际安装测试分开；先检查本机帮助，不假定增加 enabled 配置就完成安装。可在获准范围使用 `codex plugin marketplace add ./local-marketplace-root` 登记本地市场，路径替换为实际完整包或市场根；登记可能修改宿主配置，不作为无副作用测试。

在桌面插件目录选择该来源并执行实际安装。按客户端要求刷新或新建获准测试会话，核对来源路径、版本、installed／enabled 状态及两个 Skill 的真实发现和读取事件。旧聊天不保证自动刷新。只有目录记录或代理自称启用不足以通过验收。

依据：[OpenAI 插件打包与安装说明](https://developers.openai.com/plugins/build/plugins)。本指南不替代实际版本的工具帮助。

## 获准的 AFD 项目接入

将完整包放入项目 `plugins/adaptive-task-router/`；保留已有同名文件和本地修改。项目根 `.agents/plugins/marketplace.json` 仅合并必要条目，不覆盖其他插件：

```json
{
  "name": "afd2-sol61",
  "interface": {"displayName": "AFD 2.0 · 智能任务调度"},
  "plugins": [
    {
      "name": "adaptive-task-router",
      "source": {"source": "local", "path": "./plugins/adaptive-task-router"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Productivity"
    }
  ]
}
```

若合入既有市场，沿用其真实市场名。插件自带市场以包根为基准，项目市场以项目根为基准，不混用 source.path。宿主支持并获准使用项目启用设置时，仅合并对应项：

```toml
[plugins."adaptive-task-router@afd2-sol61"]
enabled = true
```

该项只表达启用设置，不证明已安装或加载。项目入口按需引用执行 Skill 和 [AFD 适配](../skills/route-task/references/afd-integration.md)。固定子模型、只读帮手、禁递归等旧规则只能在明确获准的接入变更中协调更新；保留业务授权、唯一实施、发布与数据门。插件不自动编辑 AGENTS、ROLE、任务卡或合同。

## 最小宿主验收

在获准会话明确调用 `$adaptive-task-router:route-task`，按[行为场景](../tests/SCENARIOS.md)分别验证加载、实际分派、一次隔离实施交接、独立复核及停止／恢复。请求参数、原生身份和实际配置回显分别记录；未知项不能写 PASS。只读状态下不要为测试创建写入或额外原生任务。

试验仅限明确合成材料、隔离根和获准名额；不连接公司系统、NAS 或生产。宿主能力不足的场景标 blocked／not_run，不能删除能力或改预期来制造通过。未完成真实验收时保留候选状态。

## 更新、停用与回退

同一发布版本内容固定；更新修改补丁版本而不只依靠 SemVer build metadata 区分先后。保存旧完整包、来源和对应配置，再验证新包并按宿主流程更新缓存；不直接修改安装缓存。停用使用项目配置或插件界面；回退使用已保存的完整包与配置，保留业务成果和其他条目。卸载、删除缓存与删除源码分别处理。
