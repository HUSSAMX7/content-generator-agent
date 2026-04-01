from __future__ import annotations

import re
from difflib import SequenceMatcher

from graph_state import GraphState
from utils import normalize_arabic


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
HEADING_NUMBER_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s*")
TOC_LINE_RE = re.compile(r"^\d+(?:\.\d+)*\s+.+\.{3,}\s+\d+\s*$")


def _normalize_heading_text(text: str) -> str:
    text = HEADING_NUMBER_RE.sub("", text.strip())
    return normalize_arabic(text)


def _simplify_heading_text(text: str) -> str:
    simplified_words = []
    for word in _normalize_heading_text(text).split():
        if word.startswith("ال") and len(word) > 2:
            word = word[2:]
        simplified_words.append(word)
    return " ".join(simplified_words)


def _extract_markdown_headings(content: str) -> list[dict[str, int | str]]:
    headings = []
    for match in HEADING_RE.finditer(content):
        headings.append({
            "start": match.start(),
            "level": len(match.group(1)),
            "normalized_title": _normalize_heading_text(match.group(2)),
            "simplified_title": _simplify_heading_text(match.group(2)),
        })
    return headings


def _find_section_end(
    markdown_headings: list[dict[str, int | str]],
    current_idx: int,
    content_length: int,
) -> int:
    current_level = int(markdown_headings[current_idx]["level"])
    for next_heading in markdown_headings[current_idx + 1:]:
        if int(next_heading["level"]) <= current_level:
            return int(next_heading["start"])
    return content_length


def _score_section(section_text: str) -> int:
    score = 0
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if TOC_LINE_RE.match(stripped):
            continue
        score += len(stripped)
    return score


def _select_best_section(
    content: str,
    markdown_headings: list[dict[str, int | str]],
    title: str,
) -> str | None:
    normalized_title = normalize_arabic(title.strip())
    simplified_title = _simplify_heading_text(title)
    candidate_indexes = [
        idx
        for idx, heading in enumerate(markdown_headings)
        if heading["normalized_title"] == normalized_title
    ]

    if not candidate_indexes:
        fuzzy_candidates: list[tuple[int, float]] = []
        for idx, heading in enumerate(markdown_headings):
            ratio = SequenceMatcher(
                None,
                simplified_title,
                str(heading["simplified_title"]),
            ).ratio()
            if ratio >= 0.72:
                fuzzy_candidates.append((idx, ratio))

        fuzzy_candidates.sort(key=lambda item: item[1], reverse=True)
        candidate_indexes = [idx for idx, _ratio in fuzzy_candidates[:3]]

    best_section = None
    best_score = -1
    for idx in candidate_indexes:
        start = int(markdown_headings[idx]["start"])
        end = _find_section_end(markdown_headings, idx, len(content))
        section_text = content[start:end].strip()
        section_score = _score_section(section_text)

        if section_score > best_score:
            best_score = section_score
            best_section = section_text

    return best_section


def split_content_node(state: GraphState) -> GraphState:
    content = state["content"]
    headings = state["headings"]
    markdown_headings = _extract_markdown_headings(content)
    axes = []

    for title in headings:
        section_text = _select_best_section(content, markdown_headings, title)
        if not section_text:
            continue
        axes.append({"title": title, "content": section_text})

    return {"axes": axes}
