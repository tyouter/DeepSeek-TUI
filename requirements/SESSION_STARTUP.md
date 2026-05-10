# Session Startup Protocol

> AI Agent 必须在每次对话开始时执行以下步骤。此文件由 PIPELINE.md Phase 0 引用。

## 步骤

### S1. 加载约束

- [ ] 读取 `requirements/DEV_CHECKLIST.md`
- [ ] 读取 `requirements/PIPELINE.md`（本文件的 Phase 0 部分）
- [ ] 确认当前工作分支：`git branch --show-current`

### S2. 同步上游

```bash
git fetch upstream --prune --quiet
```

- [ ] 检查落后情况：

```bash
git rev-list --count ray-song-feature..upstream/main   # 上游领先多少 commit
git rev-list --count upstream/main..ray-song-feature   # 本地领先多少 commit
```

- [ ] 如果上游领先 > 0：询问用户是否 rebase
- [ ] 如果本地领先 > 0：说明有未合入 PR 的改动，标注状态

### S3. 扫描新 issue/PR

```bash
# 获取上游最近更新的 open issue
gh issue list --state open --limit 30 --json number,title,labels,updatedAt

# 获取上游最近更新的 open PR
gh pr list --state open --limit 15 --json number,title,labels,updatedAt
```

- [ ] 新 issue/PR 与 POOL.md 交叉比对
- [ ] 如有冲突/重复：在 POOL 中标注

### S4. 环境检查

```bash
python scripts/check.py quick
```

- [ ] `cargo fmt --check` 通过
- [ ] `cargo check --workspace` 通过

如果有失败 → 修复后才能继续

### S5. 状态摘要

向用户输出：

```
会话启动完成 — <时间>
├── 分支: ray-song-feature（落后上游 N commits / 领先 M commits）
├── 上游新增: N 个 issue, M 个 PR（与 POOL 去重结果）
├── 环境: cargo check ✅ / ❌
├── 进行中需求: [列表]
├── 待评审需求: [列表]
└── 已提交 PR: [列表 + 链接]
```
