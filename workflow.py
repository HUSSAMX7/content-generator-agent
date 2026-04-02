from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from graph_state import GraphState
from node.revise_headings_node import revise_headings_node
from node.read_file import extract_headings_node
from node.normalize_headings import normalize_headings_node
from node.human_review import human_review_node
from node.split_content import split_content_node
from node.save_axes_node import save_axes_node
from node.save_target_folder import save_target_folder_node


checkpointer = InMemorySaver()


def route_after_review(state: GraphState) -> str:
    return "split_content" if state.get("review_action") == "approve" else "revise_headings"


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("extract_headings", extract_headings_node) # extract headings 
    workflow.add_node("normalize_headings", normalize_headings_node) # normalize headings if like مقدمه instead of مقدمة 
    workflow.add_node("human_review", human_review_node) # Pause and send LLM-extracted headings to the caller for review.
    workflow.add_node("revise_headings", revise_headings_node) # revise headings based on human notes
    workflow.add_node("split_content", split_content_node) # split content into axes
    workflow.add_node("save_target_folder", save_target_folder_node) # save target folder
    workflow.add_node("save_axes", save_axes_node) # save axes to files


    workflow.add_edge(START, "extract_headings")
    workflow.add_edge("extract_headings", "normalize_headings")
    workflow.add_edge("normalize_headings", "human_review")
    workflow.add_conditional_edges("human_review", route_after_review)
    workflow.add_edge("revise_headings", "normalize_headings")
    workflow.add_edge("split_content", "save_target_folder")
    workflow.add_edge("save_target_folder", "save_axes")
    workflow.add_edge("save_axes", END)

    return workflow.compile(checkpointer=checkpointer)
