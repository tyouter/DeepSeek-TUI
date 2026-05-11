# Development Pipeline v1.4

> 版本: 1.4 | 最后更新: 2026-05-11 | 维护: AI Agent + tyouter
>
> 本文档定义了从需求发现到 PR 合入上游的开发流程。
> 按需加载（触发词: "开始开发", "评审需求", "提交 PR"）。
> 任何偏离必须有明确理由并记录在 RETRO.md 中。

---

## Pipeline 哲学

1. **质量门禁不可绕过** — 每个 Phase 的 exit criteria 必须满足才能进入下一 Phase
2. **每个 Phase 产出可验证的制品** — 不是"做完了"，是"产出了 X 且通过检查 Y"
3. **回滚总是可能的** — 任何破坏性操作前打 checkpoint tag
4. **Pipeline 自己也是需求** — 流程不顺畅的地方就是 [PIPELINE] 类型的 POOL 条目

---

## 流程总览

```
Phase 0: 会话启动（按需，触发词"开始开发"）
   │
   ▼
Phase 1: 需求评审（每个新需求走此流程）
   │
   ▼
Phase 2: 开发（在 ray-song-feature 上，pipeline 工具全可用）
   │
   ▼
Phase 3: 交付 PR（提取干净分支 → rebase → 提交 → 监控）
   │
   ▼
Phase M: Pipeline 改进（持续的元工作）
```

---

## Phase 0: 会话启动协议

**触发**: 用户说"开始开发" / "评审需求" / "提交 PR"（按需加载）
**执行者**: AI Agent
**依据**: `requirements/SESSION_STARTUP.md`

### Exit Criteria

- [ ] `git fetch upstream --prune --quiet` 完成
- [ ] `ray-song-feature` 相对 `upstream/main` 的落后情况已确认
- [ ] 上游新增 issue/PR 已扫描（与 POOL 去重）
- [ ] `python scripts/check.py quick` 通过（环境可用）
- [ ] 状态摘要已输出：待开发 / 进行中 / 已提交 PR / 阻塞

---

## Phase 1: 需求评审

**触发**: 用户提出新需求
**执行者**: AI Agent（评审）+ 用户（确认）

### 1.1 需求捕获

用户自然语言描述即可。AI 提炼为结构化草稿。

### 1.2 去重检查（必须）

```bash
# 搜索上游 issue
gh issue list --state open --search "<关键词>" --limit 20 --json number,title,state

# 搜索上游 PR
gh pr list --state open --search "<关键词>" --limit 20 --json number,title,state

# 搜索已有 POOL 条目（人工核对）
```

**判定结果：**

| 情况 | 动作 |
|------|------|
| 上游已有相同 issue | POOL 标注"上游已有 #NNN"，状态 → ❌ 不做 |
| 上游已有相关 PR | POOL 标注"上游 PR #NNN 已覆盖"，状态 → ❌ 不做 |
| 上游已有类似但不同 | POOL 标注关联，继续评审 |
| 完全新需求 | 继续 1.3 |

### 1.3 需求分析 & 风险评审

AI 出具**评审报告**，必须覆盖：

| 维度 | 问题 |
|------|------|
| **合法性** | 是否与上游 AGENTS.md / CONTRIBUTING.md 的要求冲突？ |
| **架构影响** | 涉及哪些 crate？是否跨模块边界？是否破坏现有接口？ |
| **安全面** | 是否引入新的攻击面？（新工具 = 新安全边界；新 shell 路径 = 注入风险；新网络调用 = SSRF 风险） |
| **依赖影响** | 是否需要新 crate？上游是否接受新依赖？ |
| **平台影响** | Windows/Linux/macOS 行为是否一致？是否有终端兼容性问题（conhost/Windows Terminal/iTerm2/Ghostty）？ |
| **可测试性** | 能否写自动化测试？是否需要 PTY 测试？ |
| **上游接受度** | 类似 PR 历史上是否被拒？是否有风格/架构偏好需要注意？ |
| **工作量** | S / M / L 评估是否合理？ |

### 1.4 用户确认

评审报告提交给用户，逐条讨论风险点。用户确认后：

- POOL 状态: `🔴 待评估` → `🟡 已评审/就绪`
- 分配需求 ID（格式：`REQ-YYYYMMDD-NNN`）

### Exit Criteria

- [ ] 去重检查完成（issue + PR + POOL）
- [ ] 评审报告已出具（覆盖全部 8 个维度）
- [ ] 风险点已与用户讨论
- [ ] POOL 条目已创建/更新，状态 = `🟡 已评审/就绪`

---

## Phase 2: 开发

**触发**: 用户选择 POOL 中状态为 `🟡 已评审/就绪` 的需求
**执行者**: AI Agent（开发）+ 用户（审查）

### 2.1 在 ray-song-feature 上开发

**所有开发在 `ray-song-feature` 上进行。这是唯一拥有 pipeline 工具的分支。**

无需创建 feature 分支——Phase 2 的全部工作（编码、检查、提交）都在
`ray-song-feature` 上完成。pipeline 工具（`scripts/check.py`、`.githooks/`、
`requirements/`）在此分支上始终可用。

```bash
# 确保在最新上游基础上
git checkout ray-song-feature
git fetch upstream
git rebase upstream/main

# 现在开始开发——所有 commit 直接落在 ray-song-feature 上
```

分支关系：
```
upstream/main
     │
     └── ray-song-feature  ← Phase 2 开发在此
              │                 (pipeline 工具可用)
              ├── commit 1
              ├── commit 2
              └── commit 3  ← 功能完成
                                │
                                ▼
                           Phase 3: 提取到干净 PR 分支
```

### 2.2 规格文档（M/L 级别需求）

对于预估 M 或 L 的需求，在 `requirements/specs/<REQ-ID>.md` 中编写：

```markdown
# <REQ-ID>: <标题>

## 目标
一句话。

## 验收标准
- [ ] 标准 1
- [ ] 标准 2

## 设计方案
### 涉及文件
### 关键接口变更
### 数据流

## 测试策略
### 单元测试
### 集成测试
### 手动验证步骤

## 安全考量
## 回滚方案
```

### 2.3 AI 编码规范

**适用于所有 AI 生成的代码。违反则必须在 RETRO 中记录。**

#### 2.3.1 增量验证原则

```
❌ 不对:  写 500 行 → 跑 cargo build（炸了，不知道哪里错）
✅ 对的:  写 1 个函数 → 编译通过 → 写测试 → 提交 → 下一个函数
```

每个 commit 应该是**原子化的、可通过编译的、可通过测试的**增量。

#### 2.3.2 Spec-before-Code

- S 级需求（< 1 天）：可以直接开发，但至少要有内联注释描述意图
- M 级需求：必须写 `specs/<ID>.md`，用户确认后再开发
- L 级需求：必须写 spec + 分阶段 review + 可能拆成多个子需求

#### 2.3.3 架构边界检查

AI 容易无意中违反模块边界。每次改动前自问：

- [ ] 这个改动是否在正确的 crate 里？
- [ ] 是否引入了新的 crate 间依赖？（需要更新 Cargo.toml 的 `[dependencies]`）
- [ ] 是否破坏了现有 public API？（会 cascading break 其他 crate）
- [ ] 是否在 UI crate 里写了业务逻辑？（应该在 core/agent）
- [ ] 是否在 core crate 里引用了 TUI 类型？（依赖倒置问题）

#### 2.3.4 Provenance 标注

- 所有新文件/函数若主要由 AI 生成，不在代码中标注（上游不接受）
- 但在 commit message 和 PR 描述中必须声明 `Developed with AI assistance`
- RETRO 中记录 AI 生成占比（大致比例即可，不需要精确）

#### 2.3.5 Deterministic Testing

- 每个新功能或修复必须有对应测试
- 测试必须：失败在前（证明测试有效）→ 通过在后（证明修复有效）
- 不接受"我手动跑了一下没问题"

### 2.4 安全审查（四层）

安全审查不是"开发完看一眼"，而是分层推进的强制流程。

#### Layer 1: 自动化扫描

```bash
# 基础编译检查
cargo check --workspace --all-targets

# Clippy（deny warnings）
cargo clippy --workspace --all-targets --all-features -- -D warnings

# 格式检查
cargo fmt --all -- --check

# 测试
cargo test --workspace --all-features
```

#### Layer 2: 模式检查清单

AI 必须逐条回答以下问题，不得跳过：

| # | 检查项 | 判断 |
|---|--------|------|
| 1 | 是否有新的 `unsafe` 块？ | 如果有 → 必须在 spec 中写清楚为什么必要、为什么安全 |
| 2 | 是否有硬编码的路径/URL/密钥？ | 如果有 → 拒绝 |
| 3 | 是否引入了新的文件系统操作？ | 如果有 → 路径校验是否防范 `..` 穿越？是否限制在 workspace 内？ |
| 4 | 是否引入了新的网络操作？ | 如果有 → SSRF 防范？URL 白名单？ |
| 5 | 是否引入了新的 shell 执行？ | 如果有 → 命令参数是否来自模型输出？是否做了 deny-list 检查？ |
| 6 | 是否修改了 subprocess 启动方式？ | 如果有 → 环境变量 scrub 是否仍然生效？ |
| 7 | 是否修改了权限/模式边界？ | 如果有 → Plan 模式仍只读？子 agent 权限不超过父 agent？ |
| 8 | 是否有 `unwrap()` / `expect()` 可能 panic？ | 如果有 → 是否真的不可达？是否有更好的错误处理？ |
| 9 | 是否引入了新的第三方依赖？ | 如果有 → 是否纯 Rust？是否有安全审计历史？是否在 PR 描述里论证了必要性？ |
| 10 | 是否有 `as` 强转可能丢失数据？ | 如果有 → 改用 `try_from` / `from`？ |

#### Layer 3: 架构级安全审查

对照上游的安全实践（参考 v0.8.23 的 security 条目），自问：

- [ ] 本改动是否打开了新的攻击面？
- [ ] 如果这个功能被恶意利用，最坏能造成什么后果？
- [ ] 本改动的权限模型是否与上游一致？（DeepSeek TUI 的安全模型：Plan 只读、Agent 审批、YOLO 全自动）
- [ ] 是否有尚未处理的 edge case？（空输入、超长输入、Unicode 边界、并发调用）

#### Layer 4: 人类审查（用户）

- [ ] 用户阅读安全审查摘要（Layer 1-3 的结果）
- [ ] 用户确认所有风险已识别并处理
- [ ] 用户批准 → 进入 Phase 3

### 2.5 Changelog 片段

在 `requirements/specs/<REQ-ID>.md` 或直接写 changelog 片段：

```markdown
### Added / Fixed / Changed

- **简短描述** (#PR编号，待填) — 详细说明。Thanks **@tyouter**.
```

### 2.6 Commit

```bash
# Atomic commits with conventional format
git add <files>
git commit -m "feat(<scope>): 简短描述

详细的 body 说明。

Refs: REQ-YYYYMMDD-NNN
Developed with AI assistance."

# commit 直接落在 ray-song-feature 上
# Phase 3 时再提取到干净的 PR 分支
```

### Exit Criteria (Phase 2)

- [ ] 所有代码已 incremental commit（在 `ray-song-feature` 上）
- [ ] Layer 1 自动化扫描全部通过
- [ ] Layer 2 模式检查清单全部完成（10 项）
- [ ] Layer 3 架构安全审查完成
- [ ] Layer 4 用户审查完成（已批准）
- [ ] Changelog 片段已写
- [ ] 已记录本需求的 commit hash 列表（用于 Phase 3 提取）

---

## Phase 3: 交付 PR

**触发**: Phase 2 所有 exit criteria 满足
**执行者**: AI Agent（生成制品）+ 用户（最终确认）

### 3.0 提取干净 PR 分支

**这是解决 pipeline 文件污染的关"键步骤。**

在 `ray-song-feature` 上开发完后，本需求的代码 commit 和 pipeline 的 commit 混在一起。
必须提取纯代码 commit 到干净分支用于 PR。

```bash
# 1. 确认当前在 ray-song-feature，已记录本需求的 commit hash 列表
git checkout ray-song-feature

# 2. 从上游最新 commit 创建干净分支
git checkout -b feat/<REQ-ID>-<slug> upstream/main

# 3. cherry-pick 本需求的所有代码 commit（按顺序）
git cherry-pick <commit-hash-1>
git cherry-pick <commit-hash-2>
git cherry-pick <commit-hash-3>

# 4. 验证干净分支不包含 pipeline 文件
git diff upstream/main --stat
# 应该只有 crates/ 等源码目录的改动，没有 requirements/ scripts/ .githooks/
```

**检查干净分支：**
```bash
# 确认没有 pipeline 文件泄露
git diff upstream/main --name-only | grep -E "^(requirements/|scripts/|\.githooks/)" && echo "❌ 泄露!" || echo "✅ 干净"
```

如果检查到 pipeline 文件泄露：说明 cherry-pick 时不小心带入了 pipeline commit。
重新创建干净分支，只 cherry-pick 代码 commit。

### 3.1 打 Checkpoint Tag

**在任何破坏性操作前**打 tag，确保可回滚：

```bash
git tag pre-pr/<REQ-ID>-v1
```

### 3.2 生成 PR 制品包（Rebase 前）

**在 rebase 之前**就生成好所有 PR 文档，这样如果 rebase 出问题，文档不丢。

```
requirements/specs/<REQ-ID>.md  ← 已有（开发阶段写的）
requirements/specs/<REQ-ID>-pr-body.md  ← 新建：PR 描述正文
requirements/specs/<REQ-ID>-changelog.md  ← 新建：changelog 条目
```

PR body 使用 `.github/PULL_REQUEST_TEMPLATE.md` 模板。

### 3.3 最后一次 Rebase

```bash
# feature 分支已基于 upstream/main，只需确保它是最新的
git checkout feat/<REQ-ID>-<slug>
git fetch upstream
git rebase upstream/main
```

**如果 rebase 有冲突：**

1. 解决冲突
2. 重新跑 Layer 1 自动化扫描
3. 如果 scan 失败 → 修复
4. 如果修复困难 → `git reset --hard pre-pr/<REQ-ID>-v1` 回到 checkpoint，分析原因，重新来

### 3.4 最终质检（Rebase 后）

```bash
python scripts/check.py full
```

**必须全部通过**。如果有任何失败：

- 检查是否是 rebase 引入的（upstream 改了签名/依赖）
- 如果是 → 适配修复
- 如果不是（自己的代码问题） → 说明 rebase 前没跑全检，流程违规

### 3.5 提交 PR

```bash
gh pr create \
  --base main \
  --repo Hmbown/DeepSeek-TUI \
  --title "feat: <简短描述>" \
  --body-file requirements/specs/<REQ-ID>-pr-body.md
```

### 3.6 监控 & 响应

- PR 提交后，每天至少检查一次是否有 review 反馈
- 每条 review comment 必须回复
- 如需修改 → 在 `ray-song-feature` 上修改，push 同一分支（PR 自动更新）
- **禁止 force-push** 除非 reviewer 明确要求

### 3.7 结果处理

| 结果 | 动作 |
|------|------|
| **合入 (Merged)** | POOL 状态 → ✅ 已完成；写 RETRO；打 `merged/<REQ-ID>` tag |
| **被拒 (Closed)** | POOL 状态 → ❌ 不做，记录原因；写 RETRO；分析原因 |
| **要求大改** | POOL 状态不变；根据反馈修改；不要 defensive |
| **长期无回应** | 7 天后礼貌 ping 一次；14 天后自问：是不是 PR 本身有问题？ |

### 3.8 回滚流程（PR 失败时）

```
git checkout feat/<REQ-ID>-<slug>
git reset --hard pre-pr/<REQ-ID>-v1    # 回到 checkpoint
# 分析问题，修改代码，解决后：
git tag pre-pr/<REQ-ID>-v2             # 新 checkpoint
# 重新走 3.3 → 3.5
```

### Exit Criteria (Phase 3)

- [ ] checkpoint tag 已打 (`pre-pr/<REQ-ID>-vN`)
- [ ] PR 制品包已生成（body + changelog）
- [ ] rebase 到最新 upstream/main 完成
- [ ] rebase 后 `check.py full` 全部通过
- [ ] PR 已通过 gh CLI 提交
- [ ] PR 链接已记录到 POOL.md

---

## Phase M: Pipeline 改进

**触发**: 持续进行；每次 feature 交付后强制执行
**执行者**: AI Agent + 用户

### M.1 Pipeline 作为需求

任何人在开发过程中遇到的流程痛点，都是 POOL 里的需求。类型标记为 `[PIPELINE]`。

示例：
```
ID: PIPELINE-001
标题: check.py 应该增加平台预检，避免 MSVC linker 问题到提交时才发现
```

### M.2 交付后复盘

每次 Phase 3 完成（合入或被拒），填写 `requirements/RETRO.md`：

```markdown
## <REQ-ID> 复盘

- **日期**: 
- **结果**: 合入 / 被拒 / 进行中
- **耗时**: Phase 1: Xh, Phase 2: Xh, Phase 3: Xh
- **Pipeline 违规**: 无 / 有哪些
- **Gate 失败次数**: Layer 1: N 次, Layer 2: N 次
- **Review 轮数**: N 轮
- **学到了什么**:
- **Pipeline 改进建议**: 
```

### M.3 Pipeline 版本管理

- `PIPELINE.md` 版本号在文件头
- 每次修改 Pipeline 本身 → 更新版本号 + 在 CHANGELOG 记录
- Pipeline 改动必须经过用户 review（和 feature 一样）

---

## Coding Protocol（编码过程管控）

> 补充 DS TUI 原生范式（PREVIEW / CHUNK / RECURSIVE + checklist_write + update_plan）。
> DS TUI 的 base.md 已定义了完整的分解和验证流程——本协议仅补充 Rust 项目特有的纪律。

### C.1 编码原则

以下 8 条原则来自 Karpathy 式 AI 协作模式，每次编码会话必须遵守：

| # | 原则 | 含义 | 违规表现 |
|---|------|------|----------|
| 1 | **先理解，再编码** | 在修改任何代码之前，先读完和理解完整的相关代码路径 | 没读文件就开始写 patch；只看了函数签名就改实现 |
| 2 | **计划先行** | 写代码前先用 2-3 句话描述方法 | 直接开始写，用户不知道你要怎么改 |
| 3 | **最小改动** | 只改解决问题必需的部分，不顺手重构无关代码 | "顺便改了一下"——禁止。重构是独立 PR |
| 4 | **测试驱动** | 先写测试（见证失败）→ 再写实现（见证通过） | 先写实现再补测试；"我手动跑了一下" |
| 5 | **迭代精化** | 每个 commit 是原子化的、可独立验证的增量 | 一个 commit 改 10 个文件做 3 件事 |
| 6 | **显式标注不确定性** | 不确定的地方主动说出来，不要猜 | "应该可以"、"大概率没问题"——禁止 |
| 7 | **记录决策** | 为什么选这个方案而不是替代方案？写进 spec 或 commit body | 代码 merge 后没人记得为什么这么设计 |
| 8 | **尊重项目惯例** | 匹配现有代码风格、模式、命名、错误处理方式 | 引入新的错误处理模式；用 `anyhow` 而项目用 `thiserror` |

### C.2 使用 DS TUI 原生工具

DS TUI 的 system prompt 已定义了完整的分解和验证流程。本 Pipeline 使用原生工具，
不另建体系：

| 需求 | 原生工具 | 用法 |
|------|----------|------|
| 工作拆解 | `checklist_write` | 每个 WBS 子任务一个 checklist 条目 |
| 高层策略 | `update_plan` | 复杂需求用 3-6 个 phase |
| 并行调查 | `agent_spawn` | 独立文件/模块的读取和搜索 |
| 批量分类 | `rlm` + `llm_query_batched` | 15+ 文件的分析 |
| 增量进度 | `checklist_update` | 标记子任务 in_progress → completed |
| Git 操作 | `exec_shell` | 原生命令（commit、rebase 等） |

**编码节奏**（遵循原生 Verification Principle）：
```
PREVIEW   → 读文件，理解代码路径
           ↓
checklist_write  → 拆解为子任务
           ↓
循环: 1 函数 → cargo check → cargo test → commit
（cargo check 连续 2 次失败 → 停下来，不要盲目改）
           ↓
checklist_update → 标记完成

### C.3 上下文工程（Context Engineering）

**编码前必须做上下文准备，不是"打开文件就开始写"。**

```
Step 1: 确定最小上下文集合
  "为了完成这个子任务，我需要理解哪些文件？"

Step 2: 加载上下文
  ├── 目标文件（要修改的文件）
  ├── 调用者（谁在调用要修改的代码）
  ├── 被调用者（要修改的代码调用了谁）
  ├── 同级参考（相同 crate 内类似的实现作为风格参考）
  └── 测试文件（已有测试，理解预期行为）

Step 3: 验证理解
  ├── 向用户输出：已读了哪些文件，关键发现是什么
  └── 如果理解有误，用户在 Phase A 就可以纠正
```

**上下文加载量控制：**

| 子任务复杂度 | 预加载文件数 | 策略 |
|-------------|-------------|------|
| S（< 2h） | 2-4 个文件 | 直接 read_file |
| M（2-6h） | 5-10 个文件 | 关键文件直接读 + 其他用子 agent 调查 |
| L（> 6h） | 10+ 个文件 | 全部用子 agent 并行调查 → 汇总报告 |

**上下文衰减处理：**

会话变长时，AI 对早期读过的文件的记忆会衰减。对策：
- 每 5 个 turn 后，如果需要引用早期读过的文件，重新 `read_file` 确认
- 不要依赖"我记得那个文件里有……"——必须重新验证

### C.4 编码会话反模式

| 反模式 | 为什么危险 | 正确做法 |
|--------|-----------|----------|
| **探索性编码** — 不读代码，直接写 patch | 不理解架构，80% 会出错 | PREVIEW → 先读代码路径 |
| **大水漫灌** — 一次改 8 个文件 | 编译失败时不知道哪个改动是原因 | 增量循环，每次 1 个 commit |
| **跳过测试** — "这个太简单了，不需要测试" | 没有回归保护 | 先写测试（红）→ 再实现（绿） |
| **拷贝粘贴** — 从外部复制代码 | 不安全模式、不匹配的风格 | 理解后匹配项目风格重写 |
| **静默修改** — 改代码不告诉用户 | 用户失去对代码库的理解 | 每个 commit 说明 what + why |
| **死循环修复** — 反复修改反复失败 | 浪费 token，方向错误 | 2 次失败就停下来，重新理解 |

---

## Pipeline Engineering（工程管理层）

> 横切所有 Phase，定义了 AI-人协作的工程纪律。
> 不是"怎么写代码"，而是"怎么管工程"。

### E.1 需求状态机

每个需求在 POOL.md 中的生命周期是严格的状态机，不是随意切换的标签：

```
                    ┌─────────────┐
                    │  ⏸️ 阻塞    │ ← 遇到外部 blocker
                    └──────┬──────┘
                           │ blocker 解决
                           ▼
🔴 待评审 ──[Phase 1 pass]──→ 🟡 已评审/就绪
                                    │
                          [用户选择开发]
                                    ▼
                              🟢 开发中 ──[检测到 blocker]──→ ⏸️ 阻塞
                                    │
                          [Phase 2 pass]
                                    ▼
                              🟣 待交付
                                    │
                          [Phase 3 pass]
                                    ▼
                              🔵 已提交 PR
                               │         │
                    [PR merged] │         │ [PR closed / 被拒]
                               ▼         ▼
                          ✅ 已合入    ❌ 不做
```

**状态转换守卫（Guard Conditions）：**

| 转换 | 进入条件 | 产出物 |
|------|----------|--------|
| 🔴 → 🟡 | 去重完成 + 8 维评审报告 + 用户确认 | POOL 条目、评审报告 |
| 🟡 → 🟢 | 分支已创建 + spec 已写(M/L) + WBS 已分解 | spec 文档、WBS |
| 🟢 → 🟣 | Layer 1-4 全部通过 + 分支已合并 | 证据包、changelog 片段 |
| 🟣 → 🔵 | PR 制品已生成 + rebase 完成 + check.py full 通过 | PR body、PR 链接 |
| 🔵 → ✅ | upstream merged | merged tag |
| 🔵 → ❌ | upstream closed | 拒绝原因记录 |
| 🟢 → ⏸️ | 发现无法在本次解决的外部 blocker | blocker 描述 |
| ⏸️ → 🟢 | blocker 已解决（上游修复、依赖更新等） | 更新 POOL 备注 |

### E.2 工作拆解（WBS）

**M/L 级需求必须先拆解，再开发。**

WBS 模板（写入 `specs/<REQ-ID>.md`）：

```markdown
## 工作拆解 (WBS)

| # | 子任务 | 预计耗时 | 依赖 | 验收方式 |
|---|--------|----------|------|----------|
| 1 | 任务描述 | Xh | 无 / 依赖子任务 N | 编译通过 / 测试通过 / 手动操作 |
| 2 | ... | | | |
```

**拆解原则：**
- 每个子任务 ≤ 3 小时（超过则继续拆）
- 每个子任务可独立编译和验证
- 子任务按依赖关系排序（有依赖的放后面）
- 第一个子任务应是"最小可验证增量"（骨架 → 功能 → 优化）
- 拆解完成 → 用户确认 → 开始开发

### E.3 时间盒（Timeboxing）

每个 Phase 有时间预期。超出预期是警告信号，不是错误——但需要解释。

| Phase | S 级需求 | M 级需求 | L 级需求 |
|-------|---------|---------|---------|
| Phase 1 (评审) | 0.5h | 1h | 2h |
| Phase 2 (开发) | 2–6h | 1–3 天 | 1–2 周 |
| Phase 3 (交付) | 0.5h | 1h | 2h |
| Review 等待 | 1–7 天 | | |

**超时处理：**
- Phase 1 超时 → 需求可能太模糊或太大，考虑拆成多个
- Phase 2 超时 → 检查 WBS 是否合理，是否遇到了未预见的技术障碍
- Phase 3 超时 → 检查 rebase 冲突或 gate 失败是否可避免
- 任何超时 → 在 RETRO 中记录原因

### E.4 质量证据包（Evidence Package）

**Phase 2 完成时**，AI 必须生成证据包，不是只 claim "通过了"：

`requirements/specs/<REQ-ID>-evidence.md`:

```markdown
# <REQ-ID> 质量证据包

## Layer 1: 自动化扫描
<!-- 粘贴 check.py full 的完整输出 -->
```

```
[check.py full 输出]
```

## Layer 2: 安全模式检查

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | unsafe 块 | 无 / 有(N处) | 如果有时：为什么必要、为什么安全 |
| ... | (共 10 项) | | |

## Layer 3: 架构安全

- 攻击面变化: [描述]
- 最坏后果: [描述]
- 权限模型一致性: [描述]
- Edge case 处理: [描述]

## Layer 4: 用户审查

- [ ] 用户已阅读 Layer 1-3
- [ ] 用户已批准

## 测试覆盖

### 新增测试
<!-- 列出新增的测试用例和覆盖的场景 -->

### 测试输出
<!-- cargo test 中与本改动相关的部分 -->

### 手动验证记录
<!-- 如果做了手动验证，记录步骤和结果 -->

## 改动统计

- 修改文件数: N
- 新增行数: N
- 删除行数: N
- 新增依赖: 无 / [列表]
```

### E.5 上下文预算管理

**AI 上下文窗口是有限资源，需要主动管理。**

| 预算水位 | 动作 |
|----------|------|
| < 40% | 正常开发 |
| 40–60% | 开始用子 agent 分担独立任务；批量 parallel tool call |
| 60–80% | **强制检查**：是否需要 `/compact`？是否可以委托给子 agent？ |
| > 80% | **必须 `/compact`** — 不再开始新开发工作 |

**Phase 2 启动前检查：**
- [ ] 当前上下文使用率 < 60%
- [ ] 如果 ≥ 60%：建议用户 `/compact`，compact 后重新开始
- [ ] 复杂调查任务（读 3+ 文件、搜索）→ 用子 agent

**开发中每 3 个 turn 检查一次上下文。**

### E.6 交接协议（Handoff Protocol）

**AI → 用户：请求决策时**

```
格式：
1. 当前状态: 做了什么，到了哪一步
2. 需要决策: 具体问题，为什么 AI 无法自行决定
3. 选项: 2-3 个具体选项及其影响
4. 收到决策后我会: 下一步做什么
```

**反例（禁止）：**
> "这个设计你觉得怎么样？"（太模糊，用户不知道要回答什么）

**正例：**
> "WBS 拆了 4 个子任务。子任务 2 涉及修改 public API，有两种方案：
> A) 保持现有签名，内部适配（安全但代码稍冗余）
> B) 改签名，清晰但需要级联修改 3 个调用点
> 建议 B，因为签名改动是合理的改进。你同意 B 还是想保守选 A？"

**用户 → AI：批准后**

```
AI 回复：
1. 确认决策: "选 B，开始改签名"
2. 下一步: "我会先修改核心 trait，跑 cargo check 确认级联影响"
3. 执行
```

### E.7 失败模式目录

| 失败模式 | 症状 | 检测方式 | 恢复步骤 |
|----------|------|----------|----------|
| **编译失败循环** | 同一错误修复 3 次仍失败 | check.py quick 连续 3 次失败 | 停下来，重新读错误信息，向用户描述障碍，请求架构建议 |
| **测试回归** | 之前通过的测试现在失败 | check.py full 显示 FAILED | `git stash` → 确认基底是否通过 → `git bisect` 定位 → 修复 |
| **Rebase 地狱** | rebase 冲突 > 5 个文件 | git rebase 过程中大量冲突 | `git rebase --abort` → `git reset --hard pre-pr/<ID>-vN` → 分析 upstream diff → 分步 rebase |
| **上下文溢出** | 响应变慢，输出截断 | 上下文 > 80% | 立即 `/compact` → 重新加载 PIPELINE → 继续 |
| **上游 API 变更** | rebase 后编译失败 | cargo check 报类型/函数缺失 | 读 upstream CHANGELOG → 适配 → 记录到 RETRO |
| **子 agent 迷航** | 子 agent 返回不相关/错误的结果 | agent_result 与预期不符 | 取消子 agent → 缩小任务范围 → 重新 spawn |
| **决策停滞** | 用户 2 天未响应 | 时间检查 | Ping 用户一次 → 暂停此需求 → 切换到 POOL 中其他就绪需求 |
| **PR 被无声关闭** | PR 状态变为 closed 无 comment | gh pr view | 先不追问，读关闭理由 → 在 RETRO 中记录 → 分析是否需要重提 |

### E.8 需求间依赖管理

当需求 A 依赖需求 B 时：

1. B 状态必须先到达 `🟡 已评审/就绪` 甚至 `✅ 已合入`
2. POOL 中标注 A 的依赖：`依赖: <REQ-ID-B>`
3. 选择开发需求时优先解除阻塞链
4. 如果 B 被标记为 `❌ 不做`，A 自动标记 `⏸️ 阻塞`，直到找到替代方案

### E.9 进度可视性

任何时候用户问"现在什么状态"，AI 必须能回答：

```
Pipeline 状态 — <时间>
├── 已合入 PR: N 个（链接）
├── 已提交 PR: N 个（链接 + 等待天数）
├── 🟣 待交付: N 个
├── 🟢 开发中: N 个（当前: <REQ-ID>）
├── 🟡 已评审: N 个
├── 🔴 待评审: N 个
├── ⏸️ 阻塞: N 个
└── 上下文: <X>%
```

---

## 附录 A: 文件索引

| 文件 | 用途 |
|------|------|
| `requirements/PIPELINE.md` | 本文件 — Pipeline 总规范 |
| `requirements/SESSION_STARTUP.md` | 会话启动检查清单 |
| `requirements/POOL.md` | 需求池（结构化追踪） |
| `requirements/DEV_CHECKLIST.md` | AI 编码约束清单 |
| `requirements/README.md` | 新手指南 + 协作流程 |
| `requirements/RETRO.md` | 交付复盘记录 |
| `requirements/specs/` | 详细规格文档 |
| `scripts/check.py` | 门禁运行器 |
| `scripts/sync-upstream.py` | 上游同步脚本 |
| `.githooks/` | Git 钩子 |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR 模板 |

## 附录 B: Commit 规范

```
feat(<scope>): 简短描述        # 新功能
fix(<scope>): 简短描述         # Bug 修复
refactor(<scope>): 简短描述    # 重构（不改行为）
docs(<scope>): 简短描述        # 文档
chore(<scope>): 简短描述       # 构建/工具
security(<scope>): 简短描述    # 安全修复
test(<scope>): 简短描述        # 测试

scope 可选: tui, core, cli, mcp, config, tools, agent
```

## 附录 C: 严禁事项

1. ❌ **直接 push 到 upstream** — 你的 fork 是 tyouter/DeepSeek-TUI，上游是 Hmbown/DeepSeek-TUI
2. ❌ **在 merge commit 上提 PR** — 必须 rebase 到线性历史
3. ❌ **force-push PR 分支**— 除非 reviewer 要求
4. ❌ **跳过 Phase 1 去重** — 重复 PR 会被立刻关闭
5. ❌ **在 Phase 2 跳过多层安全审查** — Layer 1-4 每一项都必须有记录
6. ❌ **在未打 checkpoint tag 前 rebase** — 丢工作无法恢复
7. ❌ **PR 描述不写 Testing 部分** — 上游维护者会直接要求补充
8. ❌ **将 `requirements/`、`scripts/`、`.githooks/` 等本地 pipeline 文件包含在 PR 中** — 它们是开发工具，不是项目代码
