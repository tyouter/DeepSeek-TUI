## What

<!-- 一句话描述这个 PR 做了什么 -->

## Why

<!-- 为什么需要这个改动？解决了什么问题？ -->

## How

<!-- 实现思路，关键设计决策 -->

### 涉及文件

<!-- 列出修改的文件和原因 -->

### 架构说明

<!-- 如果有架构变化，在此说明 -->

## Testing

<!-- 如何验证这个改动正确 -->

### 自动化测试

<!-- `cargo test` 结果，新增/修改了哪些测试 -->

### 手动验证

<!-- 手动操作步骤和预期结果 -->

## Checklist

- [ ] `cargo fmt --all -- --check` 通过
- [ ] `cargo build --workspace` 通过
- [ ] `cargo clippy --workspace --all-targets --all-features -- -D warnings` 通过
- [ ] `cargo test --workspace --all-features` 通过
- [ ] 未引入新的第三方依赖 或 已在下方论证必要性
- [ ] 安全审查通过（Layer 1-4）
- [ ] CHANGELOG 条目已准备

<!-- 如果有新依赖，在此论证必要性 -->
<!-- ## New Dependencies -->
<!-- - crate-name: 为什么需要 + 为什么这个选择 -->

## Notes

<!-- 任何 reviewer 需要注意的事项 -->

---
*Developed with AI assistance. Ref: <REQ-ID>*
