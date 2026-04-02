from langgraph.types import interrupt

from graph_state import GraphState
from utils import normalized_filename


def save_target_folder_node(state: GraphState) -> GraphState:
    reply = interrupt({
        "type": "save_target_folder",
        "display": "اكتب اسم المجلد الذي تريد حفظ النتائج بداخله:",
        "input_mode": "single_line",
        "response_key": "target_folder",
    })

    raw_folder_name = str(reply.get("target_folder", "")).strip()

    if not raw_folder_name:
        raise ValueError("Target folder name is required")

    return {
        "target_folder": normalized_filename(raw_folder_name),
    }