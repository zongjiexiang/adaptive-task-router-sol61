---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-full-0.2.0+afd2.sol61.20261009.2"
applies_to: [adaptive-task-router]
supersedes: []
---

# 维护与验证

插件源码目录是维护位置，安装缓存可重建，完整 ZIP 是固定版本的分发材料。维护不依赖某个用户目录、历史 Git 标签或旧补丁。

## 内容职责

| 内容 | 位置（相对 skills/） |
| --- | --- |
| 持续启用、单次例外、关闭和交付 | route-task/SKILL.md |
| 17 个模型与档位选项 | route-task/references/model-routing.md |
| 局部求解、整合与验证选型 | route-task/references/high-effort-orchestration.md |
| 原生接口与配置回显 | route-task/references/native-dispatch.md |
| 共享名额、资源、失败、停止与恢复 | route-task/references/recursive-orchestration.md |
| 尚未启用时的建议 | suggest-task-routing/SKILL.md |

两个技能及参考维护协作正文，其他文档解释安装与验证。不要复制第二套模型表或重复通用 AGENTS。模型配置、原生角色和实际可用参数按当前工具 schema 核对；请求参数与服务端实际回显分别记录。

## 结构检查

在完整插件根运行：

```sh
python3 -B tests/check_structure.py
```

缺少 PyYAML 时，在获准的开发环境按 `requirements-dev.txt` 安装。检查覆盖清单、市场来源、技能开关、文档引用和 17 个模型选项。随包 CI 只执行结构检查，不调用模型。

有本机官方插件/技能验证器时可另外运行；其结果和本包检查、原生发现及模型行为验证分开记录。实际检查记录见 [VALIDATION.md](VALIDATION.md)。

## 行为验收

从 [测试场景](../tests/SCENARIOS.md) 选择受影响项目。每个入口包含应触发、相邻不触发和失败边界，递归与停止检查必须绑定实际调用与状态证据。测试 fixture 只含合成材料，其中 pricing.py 故意包含待发现缺陷，不作为运行组件。

新行为至少验证一个代表性完整工作流；未获准或未运行模型任务时，明确留下未测项。模拟摘要不能证明真实上下文压缩，调用请求不能证明服务端采用了请求模型，静态规则不能证明真实权限隔离。

## 打包

打包完整源码、许可证、安装说明和当前核验记录，保留隐藏的插件清单及市场文件。排除 .git、个人配置、凭据、绝对私有路径、原始会话和临时测试产物。核对 ZIP 条目及逐文件 SHA-256，再从解压件执行结构检查。

每次更新内容使用新的本地缓存版本，保持同一版本内容固定。按 [安装指南](INSTALLATION.md) 更新或回退；本地包制作不自动授权推送、全局安装或项目启用。
