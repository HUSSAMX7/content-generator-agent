from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from graph_state import GraphState
from node.read_file import read_file_node
from node.save_axes_node import save_axes_node

checkpointer = InMemorySaver()


def create_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("read_file", read_file_node)
    workflow.add_node("save_axes", save_axes_node)



    workflow.add_edge(START, "read_file")
    workflow.add_edge("read_file", "save_axes")
    workflow.add_edge("save_axes", END)

    return workflow.compile(checkpointer=checkpointer)

    