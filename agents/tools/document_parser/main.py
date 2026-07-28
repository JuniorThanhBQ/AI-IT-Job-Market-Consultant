import os
from pathlib import Path
from docling.document_converter import DocumentConverter


def parse_document(file_path: str, parser_type: str):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    ext = Path(file_path).suffix.lower()

    if parser_type == "cv":
        if ext not in [".pdf", ".docx"]:
            print(
                f"Error: Unsupported CV format '{ext}'. Only .pdf and .docx are allowed."
            )
            return

    elif parser_type == "image":
        if ext not in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            print(f"Error: Unsupported Image format '{ext}'.")
            return

    else:
        print(f"Error: Unknown parser type '{parser_type}'.")
        return

    try:
        converter = DocumentConverter()

        result = converter.convert(file_path)
        markdown_text = result.document.export_to_markdown()

        print("\n" + "=" * 60)
        print(
            f"--- PARSING RESULTS: {os.path.basename(file_path)} (Type: {parser_type}) ---"
        )
        print("=" * 60)
        print(markdown_text)
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"An error occurred during parsing: {e}")
