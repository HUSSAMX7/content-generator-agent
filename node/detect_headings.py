from __future__ import annotations

import re
from collections import defaultdict

from graph_state import GraphState


def detect_headings_node(state: GraphState) -> GraphState:
    content = state["content"]
    headings_by_level: dict[int, list[str]] = defaultdict(list)

    for match in re.finditer(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        if title and title not in headings_by_level[level]:
            headings_by_level[level].append(title)

    return {"detected_headings": dict(headings_by_level)}
