from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from graph_state import GraphState
from node.read_file import extract_headings_node
from node.normalize_headings import normalize_headings_node
from node.human_review import human_review_node
from node.split_content import split_content_node
from node.save_axes_node import save_axes_node

checkpointer = InMemorySaver()


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("extract_headings", extract_headings_node)
    workflow.add_node("normalize_headings", normalize_headings_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("split_content", split_content_node)
    workflow.add_node("save_axes", save_axes_node)

    workflow.add_edge(START, "extract_headings")
    workflow.add_edge("extract_headings", "normalize_headings")
    workflow.add_edge("normalize_headings", "human_review")
    workflow.add_edge("human_review", "split_content")
    workflow.add_edge("split_content", "save_axes")
    workflow.add_edge("save_axes", END)

    return workflow.compile(checkpointer=checkpointer)
