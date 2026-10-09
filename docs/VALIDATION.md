---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-0.2.1+afd2.sol61.20261009.1"
applies_to: [adaptive-task-router]
supersedes: []
---

# 本版核验记录

当前版本：`0.2.1+afd2.sol61.20261009.1`。本轮仅优化插件源码、文档和确定性测试，不修改 AFD 业务仓库、用户配置或本机安装。

## 本轮实际执行

在独立 Linux / Python 3.13.5 环境运行：

```sh
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

27 个 unittest 测试通过，退出码 0；部分测试包含多个子案例。覆盖全部模型选项解析、追加／替换错误型号、未知档位、重复／缺失、围栏示例、损坏清单／YAML、入口开关、缺失文件、包内兄弟引用、越界引用以及 CLI JSON／退出码。测试只在合成临时目录运行，不调用模型或业务。

这是本轮实现者自测，不是独立 Pro 复核。机器可读记录见 `docs/revision-validation.json`。本地未通过网络克隆完整仓库，因此不将本地夹具检查称为完整包结构检查；随包 CI 会在完整提交上运行回归、结构检查和差异检查，其状态以对应 GitHub run 为准，不从工作流文件推断通过。

## 本轮未执行

未安装到用户的 Codex，未验证实际 Skill 加载、模型／角色回显、实施型帮手、递归、真实停止恢复或上下文压缩；没有真实 AFD 维修、业务恢复、通知、自然节点或性能／费用对照。AFD 接入场景见[行为场景](../tests/SCENARIOS.md)，未执行项保持 not_run，不将文档或模拟当原生证明。

原生参数已改为按实际 schema 核对；不保证所有客户端具有同一字段。项目授权、写入权及发布围栏继续依赖实际受控入口，行为规则不代替技术隔离。

## 上一候选记录（保留，不能归入本轮）

原候选 `0.2.0+afd2.sol61.20261009.2`、基线提交 `7fd3efb866e6f79cd0d3d14ea282635030cd53c2` 的制作方结果仍保存在 `docs/validation-results.json`：完整包结构记录为 15 文档／27 本地链接／17 选项；三个变异拒绝用例；原生目录查询 installed=false、enabled=false、skills_found=0。

此前单 Skill 检查器拒绝两个技能间的兄弟目录链接；完整插件包检查允许包内引用。该历史结果没有被重写成安装成功、当前版本完整包通过或实际模型运行成功。原作其他未改文件的来源元数据保留其原日期。
