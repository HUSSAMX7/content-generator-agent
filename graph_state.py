from typing import NotRequired, TypedDict


class GraphState(TypedDict):
    content: str
    file_name: NotRequired[str]
    axes: NotRequired[list[dict]]

