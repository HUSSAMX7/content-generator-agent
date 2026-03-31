from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm
from llm_schema import NormalizedHeadings

SYSTEM_PROMPT = """\
You are given a list of Arabic document section headings that were extracted by another model.

Your task: clean and normalize these headings so they are consistent and suitable as canonical axis names.

Rules:
1) Remove any leading numbers, dots, or dashes. Example: "3 ارتباط الحل" → "ارتباط الحل"
2) Normalize common Arabic spelling variations:
   - تاء مربوطة vs هاء: treat "مقدمة" and "مقدمه" as the same → prefer the standard spelling with ة
   - همزة variations: أ/إ/آ → prefer the most standard form
   - الف مقصورة vs ياء: ى/ي → prefer the standard form
3) Remove any markdown symbols (# or *)
4) Trim extra whitespace
5) If two headings mean the same thing but are worded slightly differently, unify them to ONE canonical form
6) Keep the Arabic text — do NOT translate
7) Return the cleaned headings in the same order
"""


def normalize_headings_node(state: GraphState) -> GraphState:
    headings = state["headings"]
    headings_text = "\n".join(f"- {h}" for h in headings)

    structured_llm = llm.with_structured_output(NormalizedHeadings)
    response = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Here are the headings to normalize:\n\n{headings_text}"),
    ])
    return {"headings": response.headings}
