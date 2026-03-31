from typing import NotRequired, TypedDict


class GraphState(TypedDict):
    content: str
    file_name: NotRequired[str]
    headings: NotRequired[list[str]]
    axes: NotRequired[list[dict]]
