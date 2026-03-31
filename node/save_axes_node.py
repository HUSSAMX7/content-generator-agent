import os

from graph_state import GraphState
from utils import normalized_filename


def save_axes_node(state: GraphState) -> GraphState:
    output_dir = "axes"
    os.makedirs(output_dir, exist_ok=True)

    for axis in state["axes"]:
        filename = f"{normalized_filename(axis['title'])}.txt"
        filepath = os.path.join(output_dir, filename)

        example_num = 1
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                example_num = f.read().count("===== example") + 1

        source_file = state.get("file_name", "unknown")

        block = (
            f"===== example {example_num} =====\n"
            f"source_file: {source_file}\n"
            f"axis: {axis['title']}\n\n"
            f"{axis['content'].strip()}\n\n"
        )

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(block)

    return state
