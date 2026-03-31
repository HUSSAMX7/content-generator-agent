from __future__ import annotations

import re

from graph_state import GraphState


def _find_all_heading_positions(content: str) -> list[int]:
    """Find positions of ALL markdown headings in the document."""
    return [m.start() for m in re.finditer(r"^#{1,6}\s+", content, re.MULTILINE)]


def _find_heading_position(content: str, title: str) -> int:
    """Find heading position, handling markdown # prefixes and numbering like '2 الحل'."""
    pattern = r"^#{1,6}\s*(?:\d+\.?\s*)?" + re.escape(title)
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.start()

    idx = content.find(title)
    return idx


def _find_next_boundary(all_positions: list[int], after: int) -> int | None:
    """Find the first heading position strictly after `after`."""
    for pos in all_positions:
        if pos > after:
            return pos
    return None


def split_content_node(state: GraphState) -> GraphState:
    content = state["content"]
    headings = state["headings"]
    all_heading_positions = _find_all_heading_positions(content)
    axes = []

    for i, title in enumerate(headings):
        start = _find_heading_position(content, title)
        if start == -1:
            continue

        # Try the next confirmed heading first
        end = None
        if i + 1 < len(headings):
            next_confirmed = _find_heading_position(content, headings[i + 1])
            if next_confirmed > start:
                end = next_confirmed

        # Fallback: find the next ANY heading in the document after this section
        if end is None:
            end = _find_next_boundary(all_heading_positions, start) or len(content)

        section_text = content[start:end].strip()
        axes.append({"title": title, "content": section_text})

    return {"axes": axes}
