import os
from pathlib import Path

from dotenv import load_dotenv
from langgraph.types import Command
from llama_parse import LlamaParse

from workflow import create_workflow

load_dotenv()


def read_document_to_text(file_path: str) -> str:
    clean_path = file_path.strip().strip('"').strip("'")
    path = Path(clean_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_PARSE_API_KEY"),
            result_type="markdown",
            language="ar",
            use_vendor_multimodal_model=True,
            vendor_multimodal_model_name="openai-gpt4o",
        )
        documents = parser.load_data(str(path))
        text = "\n\n".join(doc.text for doc in documents)
    except Exception as e:
        print(f"LlamaParse error: {e}. Falling back to standard parsing...")
        import docx
        doc = docx.Document(str(path))
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)

    if not text.strip():
        raise ValueError("Document is empty after parsing.")
    return text


def prompt_user_for_headings(headings: list[str]) -> list[str]:
    """Let the user confirm, add, or remove headings."""
    print("\n" + "=" * 50)
    print("Extracted headings:")
    print("=" * 50)
    for i, h in enumerate(headings, 1):
        print(f"  {i}. {h}")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("  [Enter] = Confirm list")
        print("  [a]     = Add a new heading")
        print("  [d N]   = Delete heading by number (e.g., d 3)")
        print("  [q]     = Quit")

        choice = input("\nSelect: ").strip().lower()

        if choice == "":
            print(f"\nConfirmed {len(headings)} headings.")
            return headings

        elif choice == "a":
            new_heading = input("Enter new heading title: ").strip()
            if new_heading:
                headings.append(new_heading)
                print(f"  + Added: {new_heading}")

        elif choice.startswith("d "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(headings):
                    removed = headings.pop(idx)
                    print(f"  - Removed: {removed}")
                else:
                    print("  ! Invalid number")
            except (ValueError, IndexError):
                print("  ! Invalid format. Use: d 3")

        elif choice == "q":
            raise SystemExit("Operation cancelled.")

        else:
            print("  ! Unknown option")

        print("\nCurrent list:")
        for i, h in enumerate(headings, 1):
            print(f"  {i}. {h}")


def main():
    load_dotenv()
    file_path = r"C:\Users\hosam\OneDrive\سطح المكتب\قياس\a.docx"
    if not file_path:
        raise SystemExit("No file path provided.")

    content = read_document_to_text(file_path)
    file_name = Path(file_path).name

    app = create_workflow()
    config = {"configurable": {"thread_id": file_name}}

    # Phase 1: LLM extracts headings → graph pauses at human_review
    print("\nExtracting headings (LLM)...")
    app.invoke(
        {"content": content, "file_name": file_name},
        config=config,
    )

    # Read interrupt data
    state = app.get_state(config)
    headings = state.values.get("headings", [])

    if not headings:
        raise SystemExit("No headings extracted.")

    # User confirms / adds / removes
    confirmed = prompt_user_for_headings(list(headings))

    if not confirmed:
        raise SystemExit("No headings confirmed.")

    # Phase 2: resume → split content (Python) → save files
    print("\nSplitting content and saving files...")
    result = app.invoke(
        Command(resume=confirmed),
        config=config,
    )

    print("\nSaved successfully!")
    for axis in result.get("axes", []):
        print(f"  -> {axis['title']}")


if __name__ == "__main__":
    main()
