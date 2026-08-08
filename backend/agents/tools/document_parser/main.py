import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_document(file_path: str, parser_type: str) -> dict:
    res = {
        "text": "",
        "exceed_page_limit": False,
        "structure_illogical": False,
        "bad_text_recognition": False,
    }

    if not os.path.exists(file_path):
        res["text"] = "File does not exist."
        return res

    ext = Path(file_path).suffix.lower()

    if parser_type == "cv":
        if ext not in [".pdf", ".docx"]:
            res["structure_illogical"] = True
            return res
    elif parser_type == "image":
        if ext not in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return res
    else:
        return res

    file_size = os.path.getsize(file_path)
    if file_size > 3 * 1024 * 1024:
        res["exceed_page_limit"] = True

    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        converted = converter.convert(file_path)
        markdown_text = converted.document.export_to_markdown()
        res["text"] = markdown_text

        text_lower = markdown_text.lower()
        required_keywords = [
            "experience",
            "education",
            "skills",
            "project",
            "kinh nghiệm",
            "học vấn",
            "kỹ năng",
            "dự án",
        ]
        matches = [k for k in required_keywords if k in text_lower]
        if len(matches) < 2:
            res["structure_illogical"] = True

        if not markdown_text.strip():
            res["bad_text_recognition"] = True
        else:
            non_ascii = len(re.findall(r"[^\x00-\x7F]", markdown_text))
            total = len(markdown_text)
            if non_ascii / total > 0.4 and "kinh nghiệm" not in text_lower:
                res["bad_text_recognition"] = True

    except Exception:
        logger.exception("Docling converter failed, using basic text fallback")
        if ext == ".docx":
            try:
                import docx

                doc = docx.Document(file_path)
                fullText = []
                for para in doc.paragraphs:
                    fullText.append(para.text)
                txt = "\n".join(fullText)
                res["text"] = txt
                txt_lower = txt.lower()
                required_keywords = [
                    "experience",
                    "education",
                    "skills",
                    "project",
                    "kinh nghiệm",
                    "học vấn",
                    "kỹ năng",
                    "dự án",
                ]
                matches = [k for k in required_keywords if k in txt_lower]
                if len(matches) < 2:
                    res["structure_illogical"] = True
                if not txt.strip():
                    res["bad_text_recognition"] = True
            except Exception:
                res["bad_text_recognition"] = True
        elif ext == ".pdf":
            try:
                import pypdf

                reader = pypdf.PdfReader(file_path)
                pages_count = len(reader.pages)
                if pages_count > 3:
                    res["exceed_page_limit"] = True
                fullText = []
                for page in reader.pages:
                    fullText.append(page.extract_text() or "")
                txt = "\n".join(fullText)
                res["text"] = txt
                txt_lower = txt.lower()
                required_keywords = [
                    "experience",
                    "education",
                    "skills",
                    "project",
                    "kinh nghiệm",
                    "học vấn",
                    "kỹ năng",
                    "dự án",
                ]
                matches = [k for k in required_keywords if k in txt_lower]
                if len(matches) < 2:
                    res["structure_illogical"] = True
                if not txt.strip():
                    res["bad_text_recognition"] = True
            except Exception:
                res["bad_text_recognition"] = True

    return res
