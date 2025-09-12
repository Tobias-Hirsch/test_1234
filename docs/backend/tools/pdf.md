# `tools/pdf.py` - PDF 处理工具

本文档描述了 `backend/app/tools/pdf.py` 文件，该文件包含了用于处理 PDF 文档的工具函数，特别是将 PDF 内容转换为 Markdown 格式。

## 功能描述
*   **PDF 到 Markdown 转换**: 将 PDF 文件中的文本内容提取并转换为 Markdown 格式。
*   **文本提取**: 从 PDF 页面中提取文本。
*   **图像处理（可选）**: 如果需要，可能包含处理 PDF 中图像的逻辑。

## 逻辑实现
该模块通常会使用 `PyPDF2` 或 `pymupdf` (fitz) 等库来读取 PDF 文件并提取其内容。

例如，使用 `PyPDF2` 进行 PDF 文本提取和简单 Markdown 转换：
```python
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)

def deal_to_md(pdf_path: str) -> str:
    """
    Extracts text from a PDF file and converts it into a simple Markdown format.
    """
    markdown_content = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            num_pages = len(reader.pages)
            for i in range(num_pages):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    markdown_content.append(f"## Page {i + 1}\n\n")
                    markdown_content.append(text.strip())
                    markdown_content.append("\n\n---\n\n") # 分隔符
            logger.info(f"Successfully processed PDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Error processing PDF file {pdf_path}: {e}")
        raise
    return "\n".join(markdown_content)

# 另一个可能的实现是使用 pymupdf (fitz)
# import fitz # PyMuPDF

# def deal_to_md_pymupdf(pdf_path: str) -> str:
#     markdown_content = []
#     try:
#         doc = fitz.open(pdf_path)
#         for page_num in range(doc.page_count):
#             page = doc.load_page(page_num)
#             text = page.get_text("text") # "text" for plain text, "html", "json", "xml"
#             if text:
#                 markdown_content.append(f"## Page {page_num + 1}\n\n")
#                 markdown_content.append(text.strip())
#                 markdown_content.append("\n\n---\n\n")
#         doc.close()
#         logger.info(f"Successfully processed PDF with PyMuPDF: {pdf_path}")
#     except Exception as e:
#         logger.error(f"Error processing PDF file {pdf_path} with PyMuPDF: {e}")
#         raise
#     return "\n".join(markdown_content)
```

## 路径
`/backend/app/tools/pdf.py`