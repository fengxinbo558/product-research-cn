# 产品研究设计 Skill

用于在数据尚未采集或需要补采时，把产品决策转成可执行的研究问题、方法、样本、招募、分析和停止规则。

## 适合处理

- 研究立项与方案审查
- 生成式、评估式和验证式方法选择
- 样本覆盖、追加与停止条件
- 证据到决策规则、伦理和数据计划

已有多份材料需要综合、完整可用性测试、现有问卷统计或市场规模估算时，应使用相应专项 Skill。

## 使用

在 Codex 中直接调用：

```text
$product-research-cn 为这个产品决策设计一份可执行的研究方案。
```

安装到个人 Skill 目录的一种方式：

```bash
git clone https://github.com/fengxinbo558/product-research-cn.git ~/.codex/skills/product-research-cn
```

若目标目录已经存在，请先自行检查，不要直接覆盖。

## 内容

- `SKILL.md`：主入口、路由、模式与安全边界
- `agents/openai.yaml`：中性中文 UI 元数据
- `assets/` 与 `references/`：研究计划和方法参考
- `scripts/`：确定性的研究设计与样本规划辅助脚本
- `evals/`：触发与行为样例

## 验证与来源

本仓库版本已通过结构、安全、链接、脚本和隔离安装检查。来源和修改边界见 `UPSTREAM.md`，适用许可证原文见 `LICENSE.upstream`；这些文件属于法律与诚实溯源记录，不应删除。
