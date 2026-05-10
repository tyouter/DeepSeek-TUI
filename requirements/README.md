# 需求池 & 协作工作流

> Pipeline v1.2 | 2026-05-11

## 快速导航

| 你想做什么 | 看这个文件 |
|------------|-----------|
| 了解完整开发流程 | **[PIPELINE.md](PIPELINE.md)** — 从需求到 PR 的全流程规范 |
| 提交一个新需求 | **[POOL.md](POOL.md)** — 需求池，我来帮你填 |
| 每次编码前我读的约束 | **[DEV_CHECKLIST.md](DEV_CHECKLIST.md)** — AI 编码约束 + 安全审查清单 |
| 每次对话开始我做的事 | **[SESSION_STARTUP.md](SESSION_STARTUP.md)** — 会话启动协议 |
| 回顾某次交付的经验 | **[RETRO.md](RETRO.md)** — 交付复盘记录 |
| 看某个需求的详细设计 | **[specs/](specs/)** — 规格文档目录 |
| 怎么协作（新手向） | 继续往下读 ↓ |

---

## 协作方式（一句话版）

> 你告诉我哪里不好用 → 我评审并整理到 POOL → 我们一起选 → 我开发 → 你审查安全 → 我提 PR。

详细流程见 [PIPELINE.md](PIPELINE.md)。

---

## 工具命令速查

```bash
# 安装 git hooks（一次性）
.githooks\setup.bat

# 查看上游最新状态
python scripts/sync-upstream.py

# 跑质量门禁
python scripts/check.py quick      # 快速（fmt + check）
python scripts/check.py full       # 全套（fmt + check + build + clippy + test）
```

---

## 要点重申

1. 一个 PR 只做一件事
2. 开发前先 rebase 到最新 upstream/main
3. 提交前打 checkpoint tag
4. 安全审查四层（Layer 1-4）必须全部完成
5. PR 描述包含 Testing 证据
6. 每次交付后写复盘

## AI 声明

本项目所有代码由 AI Agent 辅助生成，tyouter 审查。每个 commit 和 PR 均包含 `Developed with AI assistance` 声明。
