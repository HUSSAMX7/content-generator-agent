from typing import NotRequired, TypedDict


class GraphState(TypedDict):
    content: str
    headings: NotRequired[list[str]]

