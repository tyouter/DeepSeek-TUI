# 需求池 & 协作工作流

> Pipeline v1.4 | 2026-05-11

## 快速导航

| 你想做什么 | 看这个文件 | 何时加载 |
|-----------|-----------|----------|
| 了解完整开发流程 | **[PIPELINE.md](PIPELINE.md)** | 说"开始开发" / "评审需求" |
| 提交新需求 | **[POOL.md](POOL.md)** | 同上 |
| 编码前检查清单 | **[DEV_CHECKLIST.md](DEV_CHECKLIST.md)** | 同上 |
| 同步上游 + 状态检查 | **[SESSION_STARTUP.md](SESSION_STARTUP.md)** | 同上 |
| 交付复盘 | **[RETRO.md](RETRO.md)** | PR 合入/被拒后 |
| 需求详细设计 | **[specs/](specs/)** | 按需 |

**Pipeline 是按需加载的**——普通对话不触发，只在说"开始开发"、"评审需求"、"提交 PR"时加载。

---

## 工具命令速查

```bash
.githooks\setup.bat                    # 安装 git hooks（一次性）
python scripts/sync-upstream.py        # 查看上游状态
python scripts/check.py quick          # 快速检查（fmt + check）
python scripts/check.py full           # 全套检查
```

---

## 核心规则

1. 一个 PR 只做一件事
2. 开发前 rebase 到最新 upstream/main
3. 提交前打 checkpoint tag（`pre-pr/<ID>-vN`）
4. 四层安全审查（Layer 1-4）全部完成
5. PR 包含 Testing 证据
6. 代码 commit 在 `ray-song-feature`，PR 时 cherry-pick 到干净分支
7. 不将 pipeline 文件带入 PR
