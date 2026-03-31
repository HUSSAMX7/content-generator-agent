from __future__ import annotations

from graph_state import GraphState

METADATA_KEYWORDS = [
    "معلومات الوثيقة",
    "تواريخ إصدارات",
    "مراجعات الوثيقة",
    "جدول المحتويات",
    "قائمة الأشكال",
    "المراجعة",
    "الاعتماد",
]


def _is_metadata(title: str) -> bool:
    lower = title.strip()
    return any(kw in lower for kw in METADATA_KEYWORDS)


def confirm_headings_node(state: GraphState) -> GraphState:
    detected: dict[int, list[str]] = state["detected_headings"]

    if not detected:
        raise ValueError("No headings detected in the document.")

    sorted_levels = sorted(detected.keys())

    while True:
        print("\n" + "=" * 60)
        print("المحاور المكتشفة حسب المستوى:")
        print("=" * 60)

        for level in sorted_levels:
            titles = detected[level]
            print(f"\n--- Level {level} ({'#' * level}) --- ({len(titles)} عنوان)")
            for i, title in enumerate(titles, 1):
                marker = "  [meta]" if _is_metadata(title) else ""
                print(f"  {i}. {title}{marker}")

        print(f"\nاختر رقم المستوى ({', '.join(str(l) for l in sorted_levels)}): ", end="")
        choice = input().strip()

        if not choice.isdigit() or int(choice) not in detected:
            print("اختيار غير صحيح، حاول مرة أخرى.")
            continue

        chosen_level = int(choice)
        chosen_titles = [t for t in detected[chosen_level] if not _is_metadata(t)]

        print(f"\n--- المحاور المختارة (Level {chosen_level}) ---")
        for i, title in enumerate(chosen_titles, 1):
            print(f"  {i}. {title}")

        print(f"\nهل تأكيد هذه المحاور؟ (y/n): ", end="")
        confirm = input().strip().lower()

        if confirm in ("y", "yes", "نعم"):
            return {
                "confirmed_headings": chosen_titles,
                "heading_level": chosen_level,
            }

        print("تم الرفض، أعد الاختيار...")
