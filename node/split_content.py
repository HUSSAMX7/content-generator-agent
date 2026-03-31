from __future__ import annotations

import re

from graph_state import GraphState


def _find_heading_position(content: str, title: str) -> int:
    """Find heading position, handling markdown # prefixes and numbering like '2 الحل'."""
    pattern = r"^#{1,6}\s*(?:\d+\.?\s*)?" + re.escape(title)
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.start()

    idx = content.find(title)
    return idx


def split_content_node(state: GraphState) -> GraphState:
    content = state["content"]
    headings = state["headings"]
    axes = []

    for i, title in enumerate(headings):
        start = _find_heading_position(content, title)
        if start == -1:
            continue

        if i + 1 < len(headings):
            end = _find_heading_position(content, headings[i + 1])
            if end == -1:
                end = len(content)
        else:
            end = len(content)

        section_text = content[start:end].strip()
        axes.append({"title": title, "content": section_text})

    return {"axes": axes}
