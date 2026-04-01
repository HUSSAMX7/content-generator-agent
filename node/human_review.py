from __future__ import annotations

from langgraph.types import interrupt

from graph_state import GraphState


def human_review_node(state: GraphState) -> GraphState:
    """Pause and collect a human approval or revision request."""
    headings = state["headings"]
    headings_lines = "\n".join(f"{i}. {heading}" for i, heading in enumerate(headings, 1))

    review = interrupt({
        "type": "headings_review",
        "display": (
            "هذه العناوين الحالية التي استخرجتها من المستند:\n\n"
            f"{headings_lines}\n\n"
            "اضغط Enter للموافقة، أو اكتب ملاحظاتك بحرية مثل: "
            "احذف محور كذا، أضف محور كذا، غيّر الاسم إلى كذا."
        ),
        "input_mode": "multiline",
        "empty_action": "approve",
        "revision_action": "revise",
        "response_key": "notes",
    })

    action = str(review.get("action", "approve")).strip().lower()
    notes = str(review.get("notes", "")).strip()

    if action not in {"approve", "revise"}:
        action = "approve" if not notes else "revise"

    return {
        "review_action": action,
        "human_review_notes": notes,
    }
