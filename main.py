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


def main():
    load_dotenv()
    file_path = r"C:\Users\hosam\OneDrive\سطح المكتب\قياس\a.docx"
    if not file_path:
        raise SystemExit("No file path provided.")

    content = read_document_to_text(file_path)
    file_name = Path(file_path).name

    app = create_workflow()
    config = {"configurable": {"thread_id": file_name}}

    print("\nExtracting headings (LLM)...")
    result = app.invoke(
        {"content": content, "file_name": file_name},
        config=config,
    )

    while True:
        interrupts = result.get("__interrupt__", ())
        if not interrupts:
            break

        interrupt_obj = interrupts[0]
        payload = getattr(interrupt_obj, "value", interrupt_obj)

        display = str(payload.get("display", "")).strip()
        if display:
            print(f"\nAssistant:\n{display}")

        first_line = input("\nYou: ").strip()
        if first_line.lower() in {"q", "quit", "exit"}:
            raise SystemExit("Operation cancelled.")

        empty_action = str(payload.get("empty_action", "approve")).strip().lower()
        revision_action = str(payload.get("revision_action", "revise")).strip().lower()
        response_key = str(payload.get("response_key", "notes")).strip() or "notes"

        if first_line == "" and empty_action:
            user_reply = {"action": empty_action, response_key: ""}
            print("\nAssistant: تم استلام الموافقة. سأكمل التنفيذ.")
        else:
            note_lines = [first_line] if first_line else []
            while True:
                line = input("... ").strip()
                if not line:
                    break
                note_lines.append(line)

            user_reply = {
                "action": revision_action,
                response_key: "\n".join(note_lines).strip(),
            }
            print("\nAssistant: تم استلام ملاحظاتك. سأحدّث النتيجة.")

        result = app.invoke(
            Command(resume=user_reply),
            config=config,
        )

    print("\nAssistant: تم حفظ الملفات بنجاح.")
    for axis in result.get("axes", []):
        print(f"  -> {axis['title']}")


if __name__ == "__main__":
    main()
