import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langgraph.types import Command
from llama_cloud import LlamaCloud

from workflow import create_workflow

load_dotenv()


def read_document_to_text(file_path: str, retries: int = 3, delay: int = 5) -> str:
    clean_path = file_path.strip().strip('"').strip("'")
    path = Path(clean_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    client = LlamaCloud(api_key=os.getenv("LLAMA_PARSE_API_KEY"))

    text = ""
    for attempt in range(1, retries + 1):
        try:
            file_obj = client.files.create(file=str(path), purpose="parse")
            result = client.parsing.parse(
                file_id=file_obj.id,
                tier="agentic",
                version="latest",
                output_options={
                    "markdown": {
                        "tables": {
                            "output_tables_as_markdown": True,
                        },
                    },
                },
                processing_options={
                    "ocr_parameters": {
                        "languages": ["ar"]
                    }
                },
                expand=["markdown"],
            )
            text = "\n\n".join(
                page.markdown for page in result.markdown.pages
            )
            if text.strip():
                break
            print(f"Attempt {attempt}: empty result, retrying in {delay}s...")
            time.sleep(delay)
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)

    if not text.strip():
        print("LlamaCloud returned empty. Falling back to python-docx...")
        import docx as docx_lib
        doc = docx_lib.Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs)

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
    file_path = r"C:\Users\hosam\OneDrive\سطح المكتب\قياس\b.docx"
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
