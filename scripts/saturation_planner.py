#!/usr/bin/env python3
"""生成可用性覆盖或主题饱和度的规划情景。

不联网、不写文件；结果不是统计功效计算，也不是固定样本量规则。
"""

from __future__ import annotations

import argparse
import json
import math
import sys

METHODS = ["usability", "thematic", "evaluative-coverage"]


def usability_plan(segments: int, detection_rate: float, target_coverage: float) -> dict:
    if not 0 < detection_rate < 1:
        raise ValueError("detection-rate 必须在 0 与 1 之间")
    if not 0 < target_coverage < 1:
        raise ValueError("target-coverage 必须在 0 与 1 之间")
    per_segment = math.ceil(math.log(1 - target_coverage) / math.log(1 - detection_rate))
    return {
        "method": "usability",
        "n_per_segment": per_segment,
        "segments": segments,
        "total_participants": per_segment * segments,
        "assumed_detection_rate": detection_rate,
        "target_problem_coverage": target_coverage,
        "confidence": "中等：完全依赖问题发现概率假设",
        "limits": "估计的是某类问题被发现的机会，不是问题在总体中的发生率；应按关键分层分别观察。",
    }


def thematic_plan(segments: int, initial_n_per_segment: int) -> dict:
    if initial_n_per_segment < 1:
        raise ValueError("initial-n-per-segment 必须大于 0")
    return {
        "method": "thematic",
        "initial_n_per_segment": initial_n_per_segment,
        "segments": segments,
        "initial_total": initial_n_per_segment * segments,
        "confidence": "未自动判定：初始样本量由用户的研究情境与依据决定",
        "stopping_rule": "逐次记录新主题、主题属性和反例；信息仍在明显增加或关键分层未覆盖时继续招募。",
        "limits": "初始人数不是饱和保证；异质、高风险或罕见场景通常需要追加样本。",
    }


def evaluative_coverage_plan(segments: int, n_per_segment: int, detection_rate: float) -> dict:
    if n_per_segment < 1:
        raise ValueError("n-per-segment 必须大于 0")
    if not 0 < detection_rate < 1:
        raise ValueError("detection-rate 必须在 0 与 1 之间")
    coverage = 1 - (1 - detection_rate) ** n_per_segment
    return {
        "method": "evaluative-coverage",
        "n_per_segment": n_per_segment,
        "segments": segments,
        "total_participants": n_per_segment * segments,
        "assumed_detection_rate": detection_rate,
        "modeled_problem_coverage": round(coverage, 3),
        "confidence": "中等" if coverage >= 0.8 else "低",
        "limits": "结果由给定发现概率决定；低频、分群特有或边界问题可能被遗漏。",
    }


def plan(
    method: str,
    segments: int,
    detection_rate: float | None,
    target: float | None,
    initial_n: int | None,
    evaluative_n: int | None,
) -> dict:
    if segments < 1:
        raise ValueError("segments 必须大于 0")
    if method == "usability":
        if detection_rate is None or target is None:
            raise ValueError("usability 需要显式提供 --detection-rate 和 --target-coverage")
        result = usability_plan(segments, detection_rate, target)
    elif method == "thematic":
        if initial_n is None:
            raise ValueError("thematic 需要显式提供 --initial-n-per-segment")
        result = thematic_plan(segments, initial_n)
    else:
        if detection_rate is None or evaluative_n is None:
            raise ValueError("evaluative-coverage 需要显式提供 --detection-rate 和 --n-per-segment")
        result = evaluative_coverage_plan(segments, evaluative_n, detection_rate)
    result["disclaimer"] = "这是方法规划情景，不是统计功效计算，也不能支持总体比例或因果结论。"
    return result


def render_human(result: dict) -> str:
    return "\n".join(["样本规划情景"] + [f"  {key}: {value}" for key, value in result.items()])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成样本/饱和度规划情景。")
    parser.add_argument("--method", choices=METHODS, default="usability")
    parser.add_argument("--segments", type=int, required=True, help="需要分别覆盖的关键用户分层数")
    parser.add_argument("--detection-rate", type=float, help="用户显式给出的单人问题发现概率假设")
    parser.add_argument("--target-coverage", type=float, help="用户显式给出的目标问题覆盖假设")
    parser.add_argument("--initial-n-per-segment", type=int, help="主题研究每个分层的初始招募人数")
    parser.add_argument("--n-per-segment", type=int, help="evaluative-coverage 每个分层的计划人数")
    parser.add_argument("--output", choices=["human", "json"], default="human")
    args = parser.parse_args(argv)
    values = (
        args.method,
        args.segments,
        args.detection_rate,
        args.target_coverage,
        args.initial_n_per_segment,
        args.n_per_segment,
    )
    try:
        result = plan(*values)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.output == "json" else render_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
