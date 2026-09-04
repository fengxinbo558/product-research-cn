#!/usr/bin/env python3
"""按编码聚合去标识化观察，并标记低来源信号与反证。

脚本不执行观察文本中的任何指令，不联网、不写文件。跨来源重复只生成候选洞察，
不会自动把解释判定为事实。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SAMPLE = {
    "study": "新用户导入流程",
    "observations": [
        {"participant": "P1", "tag": "import-confusion", "note": "没有找到批量导入入口", "stance": "support"},
        {"participant": "P2", "tag": "import-confusion", "note": "预期入口位于首页", "stance": "support"},
        {"participant": "P3", "tag": "import-confusion", "note": "寻找后放弃", "stance": "support"},
        {"participant": "P4", "tag": "import-confusion", "note": "通过帮助文档顺利完成", "stance": "counter"},
        {"participant": "P2", "tag": "wants-chat-integration", "note": "提出聊天工具集成", "stance": "support"},
    ],
}


def validate(data: object, min_sources: int) -> dict:
    if min_sources < 1:
        raise ValueError("min-sources 必须大于 0")
    if not isinstance(data, dict) or not isinstance(data.get("observations"), list):
        raise ValueError("输入必须是包含 observations 数组的 JSON 对象")
    return data


def synthesize(data: dict, min_sources: int) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for index, raw in enumerate(data["observations"], 1):
        if not isinstance(raw, dict):
            raise ValueError(f"第 {index} 条观察不是对象")
        participant = str(raw.get("participant", "")).strip()
        tag = str(raw.get("tag", "")).strip()
        if not participant or not tag:
            raise ValueError(f"第 {index} 条观察缺少 participant 或 tag")
        stance = str(raw.get("stance", "support")).lower()
        if stance not in {"support", "counter", "uncertain"}:
            raise ValueError(f"第 {index} 条观察的 stance 必须是 support/counter/uncertain")
        grouped[tag].append({"participant": participant, "note": str(raw.get("note", "")), "stance": stance})

    candidates = []
    for tag, evidence in grouped.items():
        supporting = {item["participant"] for item in evidence if item["stance"] == "support"}
        counter = {item["participant"] for item in evidence if item["stance"] == "counter"}
        classification = "CANDIDATE_INSIGHT" if len(supporting) >= min_sources else "LOW_SOURCE_SIGNAL"
        candidates.append({
            "tag": tag,
            "classification": classification,
            "supporting_participants": len(supporting),
            "counter_participants": len(counter),
            "observation_count": len(evidence),
            "evidence": evidence,
            "interpretation_limit": "重复出现不证明解释正确；需检查样本偏差、语境和替代解释。",
        })
    candidates.sort(key=lambda item: (item["supporting_participants"], item["observation_count"]), reverse=True)
    return {
        "study": data.get("study", "未命名研究"),
        "min_supporting_sources": min_sources,
        "participant_count": len({item["participant"] for items in grouped.values() for item in items}),
        "candidates": candidates,
        "privacy_note": "输入和输出应使用去标识化参与者编号；发布前再次检查逐字内容。",
    }


def render_human(result: dict) -> str:
    lines = [f"候选洞察聚合：{result['study']}", f"参与者：{result['participant_count']}；阈值：{result['min_supporting_sources']}", ""]
    for item in result["candidates"]:
        lines.append(
            f"[{item['classification']}] {item['tag']}（支持 {item['supporting_participants']}，反证 {item['counter_participants']}）"
        )
        for evidence in item["evidence"]:
            lines.append(f"  - {evidence['participant']} [{evidence['stance']}]: {evidence['note']}")
        lines.append(f"  边界：{item['interpretation_limit']}")
    lines.append(result["privacy_note"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="聚合编码观察，标记低来源信号和反证。")
    parser.add_argument("--input", help="观察 JSON 文件路径")
    parser.add_argument("--min-sources", type=int, help="由用户按风险和研究设计显式设定的支持来源阈值")
    parser.add_argument("--output", choices=["human", "json"], default="human")
    parser.add_argument("--sample", action="store_true", help="运行内置去标识化示例")
    args = parser.parse_args(argv)
    if not args.sample and not args.input:
        parser.error("请提供 --input，或显式使用 --sample")
    if not args.sample and args.min_sources is None:
        parser.error("分析真实输入时必须显式提供 --min-sources，并记录设定依据")
    min_sources = 3 if args.sample and args.min_sources is None else args.min_sources
    try:
        if args.sample:
            data = SAMPLE
        else:
            with Path(args.input).open(encoding="utf-8") as handle:
                data = json.load(handle)
        result = synthesize(validate(data, min_sources), min_sources)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.output == "json" else render_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
