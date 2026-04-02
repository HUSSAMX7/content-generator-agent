from typing import NotRequired, TypedDict


class GraphState(TypedDict):
    content: str
    file_name: NotRequired[str]
    headings: NotRequired[list[str]]
    axes: NotRequired[list[dict]]
    review_action: NotRequired[str]
    human_review_notes: NotRequired[str]
    target_folder: NotRequired[str]
    