from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm
from llm_schema import DocumentHeadings
from utils import clean_title

SYSTEM_PROMPT = """\
You are an expert at analyzing Arabic government digital-transformation measurement documents.

Your task: extract ONLY the titles of the primary content axes (المحاور الرئيسية).

Understanding the document structure:
- These documents have a table of contents with numbered sections like 1, 2, 3, 4...
- Each major section (axis) has sub-sections like 2.1, 2.2, 3.1, 3.2, etc.
- Headings may use # or ## or ### markdown syntax — focus on the TOP-LEVEL content sections regardless of markdown level.

Rules:
1) Return ONLY the major axes that represent actual content chapters (like مقدمة, الحل الابتكاري, المنهجية, etc.)
2) EXCLUDE all document metadata/control sections such as:
   - Document info, version dates, reviewers, approvals
   - Table of contents, list of figures/tables
   - Any section about the document itself rather than the solution content
3) EXCLUDE all sub-headings (2.1, 2.2, 3.1, 5.3, etc.) — only top-level axes
4) EXCLUDE sections like المراجعة and الاعتماد — these are document sign-off pages, not content
5) Return the heading text WITHOUT leading numbers or # symbols. For example: "2 الحل الابتكاري" → "الحل الابتكاري"
6) Return ONLY titles, no content
"""


def extract_headings_node(state: GraphState) -> GraphState:
    structured_llm = llm.with_structured_output(DocumentHeadings)
    response = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["content"]),
    ])
    headings = [clean_title(h) for h in response.headings]
    return {"headings": headings}
