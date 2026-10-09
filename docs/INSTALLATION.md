---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-full-0.2.0+afd2.sol61.20261009.2"
applies_to: [adaptive-task-router]
supersedes: []
---

# 安装与启用

先审查本包，再在获准项目安装。当前交付只完成本地候选制作；以下步骤不表示 AFD 2.0 已经接入。

## 准备

解压后保留整个 `adaptive-task-router` 目录，包括隐藏的 `.codex-plugin` 和 `.agents`。使用支持插件的 Codex 客户端，通过 `codex --version`、`codex plugin --help` 核对本机能力。结构检查需要 Python 3.10+ 与 `requirements-dev.txt` 中的 PyYAML；插件执行本身不需要 Python 服务。

本包自己的市场名是 `afd2-sol61`，插件 ID 为 `adaptive-task-router@afd2-sol61`，source 是当前包的本地路径 `.`。该入口不会从 GitHub 拉取另一份代码。版本以插件清单为准。

## AFD 2.0 项目范围接入

在项目接入获准后，将本包放入目标项目的 `plugins/adaptive-task-router/`。先保留已有同名文件和本地修改，避免覆盖其他工作。

在项目根的 `.agents/plugins/marketplace.json` 中登记这个条目。已有市场时合并条目并使用其实际市场名；不要整份覆盖已有配置。下面给出新建本地市场的完整内容：

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

在项目 `.codex/config.toml` 中合并启用项，保留其他配置：

```toml
[plugins."adaptive-task-router@afd2-sol61"]
enabled = true
```

若合入已有市场，启用项使用其实际市场名。插件目录内自带的市场以插件目录为根；上面的项目市场以项目根为根，两者的 source.path 不能混用。

项目采用完整协作规则时，还需在获准的项目入口中明确引用 `plugins/adaptive-task-router/skills/route-task/SKILL.md`，处理与固定只读帮手、禁止递归或固定子模型等旧协作约束的冲突；本包不会自动修改项目 AGENTS 或业务合同。用户后来给出的单次限制、关闭和停止指令继续有效。

打包与项目配置依据 [OpenAI 插件说明](https://developers.openai.com/plugins/build/plugins)，实际功能以当前客户端为准。

## 验收

刷新项目插件目录后，核对来源路径、版本、enabled 状态及两个技能的原生发现结果。只看到磁盘文件或清单可解析，不等于技能已载入；旧聊天也不一定自动刷新。

在需要的聊天中明确调用 `$adaptive-task-router:route-task`。已有会话接收、实际模型回显和真实派工须分别验证，不从安装结果推断。对普通外部任务或其他项目，不因本项目的启用而自动取得授权。

## 更新、停用与回退

通过维护者交付的完整新包更新，先保存现有成果、验证新包并使用新缓存版本，再按宿主标准流程刷新。不要直接修改安装缓存。

停用时使用对应项目配置或插件界面。回退使用已保存的完整包和相应项目配置，保留业务成果与其他插件条目。卸载、删除缓存、删除源码是不同操作，按实际目的处理。
