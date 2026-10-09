---
status: active
owner: AFD 2.0
last_verified: 2026-10-09
verified_commit: "adaptive-task-router-0.2.3+afd2.sol61.20261009.1"
applies_to: [adaptive-task-router]
supersedes: []
---

# 贡献指南

欢迎提交有明确复现、任务质量证据或兼容性依据的 Issue 和 Pull Request。主要文档语言是中文，英文问题也可接受。

## 修改前

阅读 README、相关技能及按需参考。保持核心技能精炼，详细策略放到对应 references。纯措辞润色不应改变启用边界、操作权限或模型选择行为。

本仓库没有运行时服务。公开说明不能把技能指令写成宿主硬保证，也不能把请求配置当作真实服务端回显。

## 本地结构检查

在仓库根目录运行，需要 Python 3.11+、Git 和 Bash：

```sh
python3 -m pip install -r requirements-dev.txt
python3 -B tests/check_structure.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

裸 `git diff --check` 只检查工作树；核验已提交内容时指定实际基线与候选：`git diff --check <base_sha> <head_sha>`。随包 GitHub Actions 执行结构、回归及事件对应的已提交差异检查。Codex 内置的插件/技能验证器可用时额外运行，结果按 [维护说明](docs/MAINTENANCE.md) 分别记录。

检查结构通过不代表模型行为通过。涉及持续启用、递归、停止恢复或选型逻辑的修改，应从 [场景](tests/SCENARIOS.md) 中挑选受影响项目，分别记录静态审查、真实调用、模拟摘要及未运行项。

## 合成测试材料

`tests/fixtures/pricing.py` **故意包含报价缺陷**，用于验证代理是否能依据原始要求独立发现问题。它不是生产代码，不应把修复该文件当作插件 bug 修复。没有明确更新评估设计时，请保留其输入和黄金规则。

## 提交要求

- 说明具体问题、最终行为及验证，不只说“更智能”。
- 不为使用代理而机械拆分，不依模型档位或多数票替代证据。
- 新增模型参考须注明支持来源与适用范围，不把旧目录或个别试验推广成普遍结论。
- 文档使用仓库相对路径或公开网址；不要提交本机绝对路径、完整会话、凭据、私人配置和运行缓存。
- 修改测试脚本时保留必要失败退出码；不要为了通过检查放宽行为验收。
- 模型调用、联网和外部写入按测试环境授权进行，CI 不默认消费模型额度。
- 使用 MIT 许可证提交贡献；第三方内容需保留适用的来源及许可证。

## 版本与发布

功能版本以插件清单为准，`+codex.<timestamp>` 只用于安装缓存。单纯补充文档不虚构新功能版本。现有标签不移动；发布说明记录目标提交、验证范围与限制。

报告问题时给出客户端版本、相关工具支持、最小输入、预期和实际行为、是否仍能复现。无需提供访问令牌或完整私人对话。
