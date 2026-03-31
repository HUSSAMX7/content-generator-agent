from __future__ import annotations

from langgraph.types import interrupt

from graph_state import GraphState


def human_review_node(state: GraphState) -> GraphState:
    """Pause execution and let the user confirm/edit the extracted headings."""
    confirmed_headings = interrupt({"headings": state["headings"]})
    return {"headings": confirmed_headings}
