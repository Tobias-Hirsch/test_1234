# `tools/inpymupdf.py` - PyMuPDF（Fitz）集成工具

本文档描述了 `backend/app/tools/inpymupdf.py` 文件，该文件可能包含了使用 PyMuPDF (Fitz) 库进行高级 PDF 处理的工具函数。

## 功能描述
*   **PDF 文本提取**: 高效地从 PDF 文档中提取文本内容。
*   **PDF 结构分析**: 可能支持分析 PDF 的结构，如页面、段落、表格等。
*   **图像提取**: 从 PDF 中提取图像。
*   **PDF 渲染**: 可能支持将 PDF 页面渲染为图像。

## 逻辑实现
该模块会直接使用 `fitz`（PyMuPDF 的导入名）库的功能。

例如，一个使用 PyMuPDF 进行 PDF 文本提取的示例：
```python
import fitz # PyMuPDF
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf_pymupdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file using PyMuPDF (fitz).
    """
    text_content = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text") # "text" for plain text
            if text:
                text_content.append(text.strip())
        doc.close()
        logger.info(f"Successfully extracted text from PDF with PyMuPDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Error extracting text from PDF file {pdf_path} with PyMuPDF: {e}")
        raise
    return "\n\n".join(text_content)

# 更多高级功能，如提取图片、渲染页面等
# def extract_images_from_pdf(pdf_path: str, output_dir: str):
#     doc = fitz.open(pdf_path)
#     for i in range(len(doc)):
#         for img in doc.get_page_images(i):
#             xref = img[0]
#             pix = fitz.Pixmap(doc, xref)
#             if pix.n - pix.alpha < 4:  # this is GRAY or RGB
#                 pix.save(os.path.join(output_dir, f"page{i}-{xref}.png"))
#             else:  # CMYK: convert to RGB first
#                 pix.set_alpha(pix.alpha)
#                 pix.save(os.path.join(output_dir, f"page{i}-{xref}.png"))
#             pix = None
```

## 路径
`/backend/app/tools/inpymupdf.py`