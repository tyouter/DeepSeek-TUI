# AI 开发约束清单（精简版）

> 按需加载。AGENTS.md 已覆盖基础约束（编译、格式、子 agent 等），本文件仅补充增量。
> 触发词: "开始开发", "评审需求", "提交 PR"

## Layer 2 安全审查（10 项）

每次代码改动必须逐条回答：

| # | 检查项 | 判断 |
|---|--------|------|
| 1 | 是否有新的 `unsafe` 块？ | |
| 2 | 是否有硬编码的路径/URL/密钥？ | |
| 3 | 是否引入了新的文件系统操作？ | |
| 4 | 是否引入了新的网络操作？ | |
| 5 | 是否引入了新的 shell 执行？ | |
| 6 | 是否修改了 subprocess 启动方式？ | |
| 7 | 是否修改了权限/模式边界？ | |
| 8 | 是否有 `unwrap()` / `expect()` 可能 panic？ | |
| 9 | 是否引入了新的第三方依赖？ | |
| 10 | 是否有 `as` 强转可能丢失数据？ | |

## Layer 3 架构安全

- [ ] 本改动是否打开了新的攻击面？
- [ ] 最坏被利用后果？
- [ ] 权限模型与上游一致？（Plan 只读 / Agent 审批 / YOLO 全自动）
- [ ] Edge case 处理？

## AI 编码规范

- [ ] 增量开发：1 函数 → 编译 → 测试 → commit → 下一个
- [ ] M/L 需求先写 spec + WBS
- [ ] 架构边界：改动在正确 crate，不跨界
- [ ] commit + PR 声明 `Developed with AI assistance`

## PR 特定

- [ ] 一个 PR 只做一件事
- [ ] 使用 `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] PR 前打 `git tag pre-pr/<REQ-ID>-vN`
- [ ] 提交前 rebase 到最新 upstream/main
- [ ] PR 描述包含 Testing 证据
- [ ] 不将 `requirements/`、`scripts/`、`.githooks/` 带进 PR

## 严禁事项

1. ❌ 跳过 upstream issue/PR 去重
2. ❌ 跳过 Layer 1-4 安全审查
3. ❌ M/L 需求不写 WBS
4. ❌ Phase 2 完成不生成证据包
5. ❌ 上下文 > 80% 继续开发不 compact
6. ❌ merge commit 提 PR
