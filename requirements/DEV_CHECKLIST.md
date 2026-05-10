# AI 开发约束清单 v2.2

> 每次开始编码工作前，AI Agent 必须阅读此文件并严格执行。
> 由 PIPELINE.md (v1.3) 引用。含编码协议 + 工程管理约束。

## 编译约束

- [ ] **不可使用 `#![feature(...)]`** — 项目要求 stable Rust 1.88+
- [ ] **不可使用 `if let` guards in match arms** — 改用 nested `if let` inside arm body（详见 AGENTS.md）
- [ ] **`let_chains`** (`if cond && let Some(x) = expr`) 在 `if`/`while` 中可用（1.88 stable）

## Phase 2 提交前必须运行（Layer 1 自动化扫描）

- [ ] `cargo fmt --all -- --check` — 格式一致
- [ ] `cargo check --workspace --all-targets` — 全部 crate 能编译
- [ ] `cargo build --workspace` — 完整编译
- [ ] `cargo clippy --workspace --all-targets --all-features -- -D warnings` — 0 warning
- [ ] `cargo test --workspace --all-features` — 测试全绿

快捷命令：`python scripts/check.py quick`（fmt + check）或 `python scripts/check.py full`（全套）

## Layer 2 安全审查清单（每次改动必须逐条回答）

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

## Layer 3 架构安全审查

- [ ] 本改动是否打开了新的攻击面？
- [ ] 如果这个功能被恶意利用，最坏能造成什么后果？
- [ ] 本改动的权限模型是否与上游一致？
- [ ] 是否有尚未处理的 edge case？

## AI 编码规范

- [ ] 增量开发：写 1 个函数 → 编译通过 → 写测试 → 提交 → 下一个
- [ ] Spec-before-Code：M/L 需求必须先写 spec
- [ ] 架构边界：改动在正确的 crate 里，不引入新的跨 crate 依赖
- [ ] Provenance：commit message 和 PR 描述声明 `Developed with AI assistance`
- [ ] Deterministic Testing：新功能/修复必须有测试，失败在前 → 通过在后

## 编码协议（Coding Protocol）

- [ ] 原则 1: 是否先读完相关代码路径才开始修改？（先理解，再编码）
- [ ] 原则 2: 是否在编码前输出了 2-3 句方法描述？（计划先行）
- [ ] 原则 3: 改动是否只包含解决当前子任务的最小变更？（最小改动）
- [ ] 原则 4: 是否先写了测试并见证了失败？（测试驱动）
- [ ] 原则 5: 当前 commit 是否只做了一件事？（迭代精化）
- [ ] Harness: M/L 需求是否定义了合约（类型/trait/测试）再实现？
- [ ] 上下文: 编码前是否加载了目标文件 + 调用者 + 被调用者？
- [ ] 上下文: 如果引用早期读过的文件，是否重新 read_file 验证？

## 工程管理约束

- [ ] M/L 需求已拆解 WBS（≤ 3h/子任务），用户已确认
- [ ] Phase 2 启动前上下文 < 60%
- [ ] 交接时使用 Handoff Protocol 格式（状态 + 决策 + 选项 + 后续）
- [ ] 超时已在 RETRO 记录原因
- [ ] Phase 2 完成时已生成证据包 (`specs/<REQ-ID>-evidence.md`)
- [ ] 状态机转换遵循 guard conditions（PIPELINE E.1）

## PR 规范

- [ ] **一个 PR 只做一件事** — 每个 feature 分支对应 POOL.md 里的一条需求
- [ ] **PR 描述使用 `.github/PULL_REQUEST_TEMPLATE.md` 模板**
- [ ] **PR 描述包含 Testing 部分** — 自动化测试 + 手动验证步骤
- [ ] **提交前 rebase 到最新 upstream/main** — 禁止 merge commit
- [ ] **PR 前打 checkpoint tag** — `git tag pre-pr/<REQ-ID>-vN`
- [ ] **PR 标题格式**：`feat:` / `fix:` / `refactor:` / `docs:` / `security:` + 简短描述
- [ ] **PR body 注明 AI assistance**

## 严禁事项

1. ❌ 直接 push 到 upstream
2. ❌ 在 merge commit 上提 PR
3. ❌ force-push PR 分支（除非 reviewer 要求）
4. ❌ 跳过 Phase 1 去重检查
5. ❌ 跳过 Layer 1-4 安全审查
6. ❌ 在未打 checkpoint tag 前 rebase
7. ❌ PR 描述不写 Testing 部分
8. ❌ M/L 需求不写 WBS 直接开始开发
9. ❌ Phase 2 完成不生成证据包
10. ❌ 上下文 > 80% 继续开发不 compact
11. ❌ 将本地 pipeline 文件（requirements/、scripts/、.githooks/）包含在 PR 中
