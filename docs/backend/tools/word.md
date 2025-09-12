# `tools/word.py` - Word 文档处理工具

本文档描述了 `backend/app/tools/word.py` 文件，该文件可能包含了用于处理 Word（.docx）文档的工具函数，例如提取文本内容。

## 功能描述
*   **Word 文本提取**: 从 Word 文档中读取文本内容。
*   **结构化提取（可选）**: 可能支持提取 Word 文档中的段落、标题、表格等结构化信息。

## 逻辑实现
该模块通常会使用 `python-docx` 等库来读取和处理 Word 文件。

例如，一个简单的 Word 文本提取示例：
```python
from docx import Document
import logging

logger = logging.getLogger(__name__)

def deal_to_text(docx_path: str) -> str:
    """
    Extracts all text from a Word (.docx) file.
    """
    extracted_text = []
    try:
        document = Document(docx_path)
        for paragraph in document.paragraphs:
            extracted_text.append(paragraph.text)
        logger.info(f"Successfully extracted text from Word: {docx_path}")
    except Exception as e:
        logger.error(f"Error processing Word file {docx_path}: {e}")
        raise
    return "\n\n".join(extracted_text)

# 更多高级功能，如提取表格、图片等
# def extract_tables_from_docx(docx_path: str) -> List[List[List[str]]]:
#     document = Document(docx_path)
#     tables_data = []
#     for table in document.tables:
#         current_table_data = []
#         for row in table.rows:
#             row_data = []
#             for cell in row.cells:
#                 row_data.append(cell.text)
#             current_table_data.append(row_data)
#         tables_data.append(current_table_data)
#     return tables_data
```

## 路径
`/backend/app/tools/word.py`