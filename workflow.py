from langgraph.graph import END, START, StateGraph

from graph_state import GraphState
from node.read_file import read_file_node


def create_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("read_file", read_file_node)
    workflow.add_edge(START, "read_file")
    workflow.add_edge("read_file", END)
    return workflow.compile()