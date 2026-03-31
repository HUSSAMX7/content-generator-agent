import os
from pathlib import Path

from dotenv import load_dotenv
from llama_parse import LlamaParse

from workflow import create_workflow

load_dotenv()

def read_document_to_text(file_path: str) -> str:
    clean_path = file_path.strip().strip('"').strip("'")
    path = Path(clean_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    parser = LlamaParse(
        api_key=os.getenv("LLAMA_PARSE_API_KEY"),
        result_type="markdown",
        language="ar",
        use_vendor_multimodal_model=True,
        vendor_multimodal_model_name="openai-gpt4o",
    )
    documents = parser.load_data(str(path))
    text = "\n\n".join(doc.text for doc in documents)

    if not text.strip():
        raise ValueError("Document is empty after parsing.")
    return text


def main():
    load_dotenv()
    file_path = r"C:\Users\hosam\OneDrive\سطح المكتب\a.docx"
    content = read_document_to_text(file_path)

    app = create_workflow()
    
    result = app.invoke({"content": content}, config={"configurable": {"thread_id": "1"}})
    for heading in result["headings"]:
        print(heading)
        
if __name__ == "__main__":
    main()
