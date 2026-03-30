from __future__ import annotations

from graph_state import GraphState
from openai import OpenAI

SYSTEM_PROMPT = """\
You are an expert at analyzing Arabic government digital-transformation measurement documents.

Your task: extract ONLY the primary content axes (المحاور الرئيسية) from the document.

Understanding the document structure:
- These documents have a table of contents with numbered sections like 1, 2, 3, 4...
- Each major section (axis) has sub-sections like 2.1, 2.2, 3.1, 3.2, etc.
- There are also document metadata sections (document info, version history, reviewers, approvals, table of figures, etc.)

Rules:
1) Return ONLY the major axes that represent actual content chapters (like مقدمة, الحل الابتكاري, المنهجية, etc.)
2) EXCLUDE all document metadata/control sections such as:
   - Document info, version dates, reviewers, approvals
   - Table of contents, list of figures/tables
   - Any section about the document itself rather than the solution content
3) EXCLUDE all sub-headings (2.1, 2.2, 3.1, 5.3, etc.) — only top-level axes
4) EXCLUDE sections like المراجعة and الاعتماد — these are document sign-off pages, not content
5) Use the EXACT heading text as it appears in the document
6) Return one heading per line, no numbering, no commentary, nothing else
"""


def read_file_node(state: GraphState) -> GraphState:
    client = OpenAI()
    response = client.responses.create(
        model="gpt-5.2",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": state["content"]},
        ],
    )
    headings = [line.strip() for line in response.output_text.splitlines() if line.strip()]
    return {"headings": headings}
