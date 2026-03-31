import json

with open('content.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    src = ''.join(cell['source'])
    if 'LlamaParse(' in src:
        cell['source'] = [
            "import os\n",
            "from dotenv import load_dotenv\n",
            "from llama_cloud_services import LlamaParse\n",
            "\n",
            "load_dotenv()\n",
            "\n",
            "pdf_path = r\"C:\\Users\\hosam\\OneDrive\\سطح المكتب\\a.docx\"\n",
            "\n",
            "parser = LlamaParse(\n",
            "    api_key=os.getenv(\"LLAMA_PARSE_API_KEY\"),\n",
            "    result_type=\"markdown\",\n",
            "    language=\"ar\",\n",
            ")\n",
        ]
        break

with open('content.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("done")
