# Session Startup Protocol

> 按需执行。当用户说"开始开发"时，加载 PIPELINE.md + DEV_CHECKLIST.md，
> 然后执行以下步骤同步状态。

## S1. 同步上游

```bash
git fetch upstream --prune --quiet
```

```bash
git rev-list --count ray-song-feature..upstream/main   # 上游领先 commit 数
git rev-list --count upstream/main..ray-song-feature   # 本地领先 commit 数
```

- 上游领先 > 0：询问用户是否 rebase
- 本地领先 > 0：标注有未合入改动

## S2. 扫描新 issue/PR

```bash
gh issue list --repo Hmbown/DeepSeek-TUI --state open --limit 30 --json number,title,labels
gh pr list --repo Hmbown/DeepSeek-TUI --state open --limit 15 --json number,title,labels
```

- 新 issue/PR 与 POOL.md 交叉比对
- 有冲突/重复 → 在 POOL 中标注

## S3. 环境检查

```bash
python scripts/check.py quick
```

- `cargo fmt --check` + `cargo check` 通过

## S4. 状态摘要

向用户输出当前 pipeline 状态（需求状态机各状态的条目数）。
