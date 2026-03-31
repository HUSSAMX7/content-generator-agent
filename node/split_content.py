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

        end = None
        for j in range(i + 1, len(headings)):
            next_pos = _find_heading_position(content, headings[j])
            if next_pos > start:
                end = next_pos
                break

        if end is None:
            end = len(content)

        section_text = content[start:end].strip()
        axes.append({"title": title, "content": section_text})

    return {"axes": axes}
