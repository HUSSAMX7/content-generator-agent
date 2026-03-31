from __future__ import annotations

from langgraph.types import interrupt

from graph_state import GraphState


def human_review_node(state: GraphState) -> GraphState:
    """Pause and send LLM-extracted headings to the caller for review."""
    confirmed_headings = interrupt({"headings": state["headings"]})
    return {"headings": confirmed_headings}
