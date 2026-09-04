#!/usr/bin/env python3
"""根据研究目标与产品阶段生成方法选择草案。

本脚本只做确定性映射，不联网、不写文件，也不代表研究已经执行。
"""

from __future__ import annotations

import argparse
import json
import sys

PROFILES = ["b2b-saas", "consumer-app", "enterprise", "marketplace", "hardware", "platform"]
GOALS = ["discovery", "evaluative", "validation"]
STAGES = ["concept", "prototype", "beta", "live"]

METHOD_MAP = {
    ("discovery", "concept"): "半结构式近期事件访谈",
    ("discovery", "prototype"): "情境观察结合生成式访谈",
    ("discovery", "beta"): "日记研究结合回访",
    ("discovery", "live"): "行为数据审查结合生成式访谈",
    ("evaluative", "concept"): "概念理解与价值感知测试",
    ("evaluative", "prototype"): "有主持可用性测试",
    ("evaluative", "beta"): "无主持可用性测试结合任务指标",
    ("evaluative", "live"): "基准可用性研究",
    ("validation", "concept"): "概念问卷或支付/投入意愿信号",
    ("validation", "prototype"): "原型偏好测试；不能替代真实行为",
    ("validation", "beta"): "经授权的意向门或需求信号测试",
    ("validation", "live"): "预先定义指标与停止规则的受控实验",
}

GUIDES = {
    "discovery": ["背景与近期情境", "最近一次真实经历", "替代方案与变通", "任务、触发与结果", "反例和收尾"],
    "evaluative": ["测试前背景", "代表性任务", "边界任务", "观察犹豫、错误与恢复", "任务后量表与复盘"],
    "validation": ["筛选与分层", "刺激材料", "理解检查", "权衡或行为信号", "预设阈值与反证条件"],
}


def design(goal: str, stage: str, profile: str) -> dict:
    if profile not in PROFILES:
        raise ValueError(f"profile 必须是：{', '.join(PROFILES)}")
    if goal not in GOALS or stage not in STAGES:
        raise ValueError("goal 或 stage 不在支持范围内")
    method = METHOD_MAP[(goal, stage)]
    return {
        "goal": goal,
        "stage": stage,
        "profile": profile,
        "recommended_method": method,
        "guide_skeleton": GUIDES[goal],
        "participant_principles": [
            "按真实任务和关键情境筛选，而不只按职位筛选。",
            "若要分群报告，每个关键分群都需有相应覆盖。",
            "记录招募渠道造成的选择偏差。",
        ],
        "limits": {
            "discovery": "可以发现和解释问题，不能估计总体发生率。",
            "evaluative": "可以发现方案问题，不能证明市场需求。",
            "validation": "只能回答设计中实际检验的假设；偏好不等于真实行为。",
        }[goal],
        "next_check": "结合决策风险、用户异质性和可用样本做人工校正。",
    }


def render_human(result: dict) -> str:
    lines = [
        f"研究设计草案：{result['goal']} / {result['stage']} / {result['profile']}",
        f"推荐方法：{result['recommended_method']}",
        "提纲：",
    ]
    lines.extend(f"  {i}. {item}" for i, item in enumerate(result["guide_skeleton"], 1))
    lines.append("参与者原则：")
    lines.extend(f"  - {item}" for item in result["participant_principles"])
    lines.extend([f"边界：{result['limits']}", f"下一步：{result['next_check']}"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成产品研究方法选择草案；不执行研究。")
    parser.add_argument("--goal", choices=GOALS, help="真实任务的研究目标")
    parser.add_argument("--stage", choices=STAGES, help="真实任务的产品阶段")
    parser.add_argument("--profile", choices=PROFILES, help="真实任务的产品类型")
    parser.add_argument("--output", choices=["human", "json"], default="human")
    parser.add_argument("--sample", action="store_true", help="运行内置示例")
    args = parser.parse_args(argv)
    if args.sample:
        goal, stage, profile = "discovery", "concept", "b2b-saas"
    else:
        missing = [
            option
            for option, value in (
                ("--goal", args.goal),
                ("--stage", args.stage),
                ("--profile", args.profile),
            )
            if value is None
        ]
        if missing:
            parser.error(f"真实模式必须显式提供：{', '.join(missing)}；仅检查格式时使用 --sample")
        goal, stage, profile = args.goal, args.stage, args.profile
    try:
        result = design(goal, stage, profile)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.output == "json" else render_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
