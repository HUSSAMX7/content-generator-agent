from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm
from llm_schema import DocumentHeadings

SYSTEM_PROMPT = """\
You are revising a list of Arabic document headings.

You will receive:
1) The full document content
2) The current extracted headings
3) Human review notes

Your task:
- Update the headings based on the user's notes
- Use the document content to verify whether the requested changes make sense
- Add missing major headings if the user asks and they are supported by the document
- Remove headings if the user asks and they are not real major axes
- Rename headings if the user asks for a better/correct wording
- Keep only the primary document axes
- Keep the headings in Arabic
- Return only the final revised headings list
"""


def revise_headings_node(state: GraphState) -> GraphState:
    content = state["content"]
    headings = state["headings"]
    review_notes = state.get("human_review_notes", "")

    headings_text = "\n".join(f"- {h}" for h in headings)
    structured_llm = llm.with_structured_output(DocumentHeadings)

    response = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Current headings:\n{headings_text}\n\n"
                f"Human notes:\n{review_notes}\n\n"
                f"Document content:\n{content}"
            )
        )
    ])

    return {
        "headings": response.headings,
        "human_review_notes": "",
    }