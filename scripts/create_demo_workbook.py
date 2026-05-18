#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from common import (
    ABSTRACT_HEADER,
    EVIDENCE_PATH_HEADER,
    FIELD_GUIDANCE_HEADER,
    FIELD_HEADER,
    FIELD_VALUE_HEADER,
    LOCAL_FILE_HEADER,
    PAPER_LINK_HEADER,
    PAPER_TITLE_HEADER,
    WARNING_HEADER,
    WRITING_EVIDENCE_HEADER,
    WRITING_SECTION_HEADER,
)


def main() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    output = skill_root / "assets" / "demo" / "literature-demo.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    paper_ws = wb.active
    paper_ws.title = "\u8bba\u6587\u8868"
    paper_ws.append(
        [
            PAPER_TITLE_HEADER,
            PAPER_LINK_HEADER,
            ABSTRACT_HEADER,
            "\u8303\u5f0f\u6620\u5c04",
            "\u8303\u5f0f\u5c0f\u7c7b",
            "\u529f\u80fd\u6620\u5c04\u5c42",
            "\u534f\u540c\u7c92\u5ea6",
            "\u662f\u5426\u4e3a\u53cc\u81c2\u9488\u5bf9\u8bbe\u8ba1",
            "\u6838\u9a8c\u540e\u6838\u5fc3\u65b9\u6cd5",
            "\u6838\u9a8c\u540e\u4efb\u52a1/\u6570\u636e\u96c6",
            "\u6838\u9a8c\u540e\u5173\u952e\u7ed3\u679c",
            "\u6838\u9a8c\u540e\u4e3b\u8981\u5c40\u9650",
            WRITING_SECTION_HEADER,
            WRITING_EVIDENCE_HEADER,
            LOCAL_FILE_HEADER,
            EVIDENCE_PATH_HEADER,
            WARNING_HEADER,
        ]
    )
    paper_ws.append(
        [
            "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control",
            "https://arxiv.org/abs/2307.15818",
            "General VLA baseline that transfers web-scale vision-language knowledge into robotic control.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    paper_ws.append(
        [
            "Demo Bimanual Policy Paper",
            "",
            "A placeholder dual-arm paper row for walkthroughs where the user can test title-only retrieval and warning behavior.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    paper_ws.append(
        [
            "Large Language Models for Orchestrating Bimanual Robots (LABOR)",
            "https://arxiv.org/abs/2404.02018",
            "An LLM-based orchestration paper for long-horizon bimanual manipulation that is useful for testing webpage fallback behavior.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )

    guide_ws = wb.create_sheet("\u5b57\u6bb5\u8bf4\u660e")
    guide_ws.append([FIELD_HEADER, FIELD_GUIDANCE_HEADER, FIELD_VALUE_HEADER])
    guide_ws.append(["\u8303\u5f0f\u6620\u5c04", "\u57fa\u4e8e\u8bba\u6587\u5168\u6587\u5224\u65ad\u67b6\u6784\u8303\u5f0f", "Paradigm I / Paradigm II"])
    guide_ws.append(["\u8303\u5f0f\u5c0f\u7c7b", "\u6309\u7528\u6237\u5b9a\u4e49\u7684\u7814\u7a76\u5206\u7c7b\u586b\u5199", "\u4ee5\u8bf4\u660e\u9875\u5177\u4f53\u53e3\u5f84\u4e3a\u51c6"])
    guide_ws.append(["\u529f\u80fd\u6620\u5c04\u5c42", "\u5224\u65ad\u8bba\u6587\u4e3b\u8981\u4f5c\u7528\u7684\u7cfb\u7edf\u5c42\u7ea7", "Data / Perception / Planning / Policy-Action / Feedback-Safety / Multil"])
    guide_ws.append(["\u534f\u540c\u7c92\u5ea6", "\u5224\u65ad\u534f\u540c\u662f\u53d1\u751f\u5728\u4efb\u52a1\u5c42\u8fd8\u662f\u52a8\u4f5c\u5c42", "Task-level / Action-level / Bimanual-coordination-level / N/A"])
    guide_ws.append(["\u662f\u5426\u4e3a\u53cc\u81c2\u9488\u5bf9\u8bbe\u8ba1", "\u5224\u65ad\u8bba\u6587\u662f\u5426\u539f\u751f\u56f4\u7ed5\u53cc\u81c2/\u53cc\u624b\u534f\u540c", "native / non-native"])
    guide_ws.append(["\u6838\u9a8c\u540e\u6838\u5fc3\u65b9\u6cd5", "\u7528\u7b80\u6d01\u81ea\u7136\u8bed\u8a00\u603b\u7ed3\u6838\u5fc3\u65b9\u6cd5", "\u4e0d\u8981\u8d85\u51fa\u8bba\u6587\u8bc1\u636e"])
    guide_ws.append(["\u6838\u9a8c\u540e\u4efb\u52a1/\u6570\u636e\u96c6", "\u6982\u62ec\u8bba\u6587\u4f7f\u7528\u7684\u4efb\u52a1\u3001\u573a\u666f\u6216\u6570\u636e\u96c6", "\u4f18\u5148\u6765\u81ea\u5168\u6587"])
    guide_ws.append(["\u6838\u9a8c\u540e\u5173\u952e\u7ed3\u679c", "\u586b\u5199\u6700\u652f\u6491\u5206\u7c7b\u6216\u65b9\u6cd5\u4ef7\u503c\u7684\u7ed3\u679c", "\u53ef\u4ee5\u662f\u5b9a\u6027\u6216\u5b9a\u91cf"])
    guide_ws.append(["\u6838\u9a8c\u540e\u4e3b\u8981\u5c40\u9650", "\u4fdd\u5b88\u63d0\u70bc\u8bba\u6587\u5c40\u9650", "\u65e0\u6cd5\u786e\u8ba4\u65f6\u7528 warning \u5217\u8bf4\u660e"])
    guide_ws.append([WRITING_SECTION_HEADER, "\u6307\u5411\u5199\u4f5c\u5927\u7eb2\u4e2d\u7684\u7ae0\u8282\u6216\u5b50\u7ae0\u8282", "\u4f8b\u5982 3.2 Taxonomy / 4.1 Representative methods"])
    guide_ws.append([WRITING_EVIDENCE_HEADER, "\u5199\u5165\u53ef\u76f4\u63a5\u670d\u52a1\u5199\u4f5c\u7684\u5177\u4f53\u8bba\u636e", "\u5305\u542b\u5177\u4f53\u65b9\u6cd5\u5dee\u5f02\u3001\u6570\u5b57\u7ed3\u679c\u6216\u8fb9\u754c\u8bf4\u660e"])

    wb.save(output)
    print(output)


if __name__ == "__main__":
    main()
