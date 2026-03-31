from __future__ import annotations

from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm

from llm_schema import DocumentAxes


SYSTEM_PROMPT = """\
You are an expert at analyzing Arabic government digital-transformation documents.

Your task: extract the primary content axes (المحاور الرئيسية) from the document,
along with the FULL text content of each axis.

Rules:
1) Extract only top-level axes (like مقدمة, الحل الابتكاري, المنهجية, etc.)
2) For each axis, include its COMPLETE text content including all sub-sections
3) EXCLUDE document metadata (info, versions, reviewers, approvals, table of contents, list of figures)
4) EXCLUDE المراجعة and الاعتماد sections
5) Use the EXACT heading text as it appears in the document
"""




def read_file_node(state: GraphState) -> GraphState:
    structured_llm = llm.with_structured_output(DocumentAxes)
    response = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["content"]),
    ])
    return {"axes": [axis.model_dump() for axis in response.axes]}