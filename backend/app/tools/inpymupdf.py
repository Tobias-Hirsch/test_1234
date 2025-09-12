import fitz
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import logging
from PIL import Image
import io
from app.utils.redis_utils import get_scan_detection_threshold

logger = logging.getLogger(__name__)

@dataclass
class LayoutElement:
    type: str  # 'text', 'image', 'table'
    content: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    metadata: Dict

@dataclass
class PageLayout:
    page_number: int
    width: float
    height: float
    elements: List[LayoutElement]

def extract_layout_with_pymupdf(pdf_path: str) -> List[PageLayout]:
    """
    使用 PyMuPDF 提取 PDF 的布局信息，包括文本、图片和表格
    """
    doc = fitz.open(pdf_path)
    layouts = []
    
    for page in doc:
        # 获取页面尺寸
        page_layout = PageLayout(
            page_number=page.number,
            width=page.rect.width,
            height=page.rect.height,
            elements=[]
        )
        
        # 1. 提取文本块（带布局信息）
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # 文本块
                # 处理文本行
                for line in block["lines"]:
                    text = " ".join([span["text"] for span in line["spans"]])
                    if text.strip():
                        element = LayoutElement(
                            type="text",
                            content=text,
                            bbox=line["bbox"],
                            metadata={
                                "font": line["spans"][0]["font"],
                                "size": line["spans"][0]["size"],
                                "color": line["spans"][0]["color"]
                            }
                        )
                        page_layout.elements.append(element)
            
            elif block["type"] == 1:  # 图片块
                # 提取图片
                for img in page.get_images(full=True):
                    try:
                        xref = img[0]
                        base_image = page.parent.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # 使用PIL处理图片
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        element = LayoutElement(
                            type="image",
                            content=f"![Image](image_{page.number}_{xref}.{base_image['ext']})",
                            bbox=block["bbox"],
                            metadata={
                                "width": base_image["width"],
                                "height": base_image["height"],
                                "format": base_image["ext"],
                                "xref": xref
                            }
                        )
                        page_layout.elements.append(element)
                    except Exception as e:
                        print(f"处理图片时出错: {e}")
        
        # 2. 检测表格
        # 使用启发式方法检测表格
        # 1. 查找对齐的文本块
        # 2. 检查是否有表格线
        # 3. 分析文本块的空间关系
        table_candidates = detect_tables(page)
        for table in table_candidates:
            element = LayoutElement(
                type="table",
                content=convert_table_to_markdown(table),
                bbox=table["bbox"],
                metadata=table["metadata"]
            )
            page_layout.elements.append(element)
        
        layouts.append(page_layout)
    
    doc.close()
    return layouts

def find_aligned_blocks(blocks: List[Dict], tolerance: int = 5) -> List[List[Dict]]:
    """
    查找对齐的文本块组，可能是表格
    """
    # 按垂直位置（y0）对块进行排序
    sorted_blocks = sorted(blocks, key=lambda b: b['bbox'][1])
    
    groups = []
    if not sorted_blocks:
        return groups
        
    current_group = [sorted_blocks[0]]
    for i in range(1, len(sorted_blocks)):
        prev_block = sorted_blocks[i-1]
        current_block = sorted_blocks[i]
        
        # 检查垂直对齐（在容差范围内）
        if abs(prev_block['bbox'][1] - current_block['bbox'][1]) < tolerance:
            current_group.append(current_block)
        else:
            if len(current_group) > 1:
                groups.append(current_group)
            current_group = [current_block]
            
    if len(current_group) > 1:
        groups.append(current_group)
        
    return groups

def has_table_lines(page: fitz.Page, block_group: List[Dict], line_threshold: int = 1) -> bool:
    """
    检查块组周围是否有表格线
    """
    if not block_group:
        return False
    
    # 计算块组的边界框
    min_x = min(b['bbox'][0] for b in block_group)
    min_y = min(b['bbox'][1] for b in block_group)
    max_x = max(b['bbox'][2] for b in block_group)
    max_y = max(b['bbox'][3] for b in block_group)
    
    # 获取页面上的所有绘图（线条）
    drawings = page.get_drawings()
    
    # 检查是否有足够多的水平或垂直线
    line_count = 0
    for path in drawings:
        for item in path["items"]:
            if item[0] == "l":  # 直线
                p1, p2 = item[1], item[2]
                # 检查是否在边界框内
                if (min_x <= p1.x <= max_x and min_y <= p1.y <= max_y) or \
                   (min_x <= p2.x <= max_x and min_y <= p2.y <= max_y):
                    line_count += 1
    
    return line_count >= line_threshold

def calculate_table_bbox(block_group: List[Dict]) -> Tuple[float, float, float, float]:
    """
    计算表格的边界框
    """
    if not block_group:
        return (0, 0, 0, 0)
    
    min_x = min(b['bbox'][0] for b in block_group)
    min_y = min(b['bbox'][1] for b in block_group)
    max_x = max(b['bbox'][2] for b in block_group)
    max_y = max(b['bbox'][3] for b in block_group)
    
    return (min_x, min_y, max_x, max_y)

def extract_table_cells(block_group: List[Dict]) -> List[List[str]]:
    """
    从块组中提取表格单元格
    """
    cells = []
    for block in block_group:
        row = []
        if "lines" in block:
            for line in block["lines"]:
                cell_text = " ".join(span["text"] for span in line["spans"])
                row.append(cell_text)
        cells.append(row)
    return cells

def detect_tables(page: fitz.Page) -> List[Dict]:
    """
    检测页面中的表格
    """
    tables = []
    
    # 1. 获取所有文本块
    blocks = page.get_text("dict")["blocks"]
    
    # 2. 查找可能的表格区域
    # 基于文本块的对齐和间距
    aligned_blocks = find_aligned_blocks(blocks)
    
    # 3. 检查是否有表格线
    for block_group in aligned_blocks:
        # 进一步过滤，确保块组看起来像表格
        if len(block_group) > 1 and has_table_lines(page, block_group):
            table = {
                "bbox": calculate_table_bbox(block_group),
                "cells": extract_table_cells(block_group),
                "metadata": {
                    "rows": len(block_group),
                    "columns": max(len(row) for row in extract_table_cells(block_group)) if block_group else 0
                }
            }
            tables.append(table)
            
    return tables

def convert_to_markdown(layouts: List[PageLayout], output_dir: str):
    """
    将布局信息转换为 Markdown 格式
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for layout in layouts:
        markdown_content = []
        
        # 添加页面标题
        markdown_content.append(f"# Page {layout.page_number + 1}\n")
        
        # 按垂直位置排序元素
        sorted_elements = sorted(layout.elements, key=lambda x: x.bbox[1])
        
        for element in sorted_elements:
            if element.type == "text":
                markdown_content.append(element.content)
            elif element.type == "image":
                # 保存图片并添加引用
                image_path = os.path.join(output_dir, f"image_{layout.page_number}_{element.metadata['xref']}.{element.metadata['format']}")
                with open(image_path, "wb") as f:
                    f.write(element.metadata["image_data"])
                markdown_content.append(element.content)
            elif element.type == "table":
                markdown_content.append("\n" + element.content + "\n")
        
        # 保存 Markdown 文件
        with open(os.path.join(output_dir, f"page_{layout.page_number + 1}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))

def convert_table_to_markdown(table: Dict) -> str:
    """
    将表格数据转换为 Markdown 格式
    """
    if not table["cells"]:
        return ""
    
    # 创建表头
    header = "| " + " | ".join(table["cells"][0]) + " |"
    separator = "| " + " | ".join(["---"] * len(table["cells"][0])) + " |"
    
    # 创建表格内容
    rows = []
    for row in table["cells"][1:]:
        rows.append("| " + " | ".join(row) + " |")
    
    return "\n".join([header, separator] + rows)

def main():
    pdf_path = "example.pdf"
    output_dir = "markdown_output"
    
    # 提取布局信息
    layouts = extract_layout_with_pymupdf(pdf_path)
    
    # 转换为 Markdown
    convert_to_markdown(layouts, output_dir)
    
    # 保存布局信息（可选）
    with open(os.path.join(output_dir, "layout_info.json"), "w", encoding="utf-8") as f:
        json.dump([layout.__dict__ for layout in layouts], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

# --- New functions for fast text extraction for chat ---

def is_scanned_pdf(doc: fitz.Document) -> bool:
    """
    Checks if a PDF is likely scanned by analyzing its text content.
    A low character count per page suggests a scanned document.
    The threshold is dynamically fetched from Redis.
    """
    SCAN_DETECTION_THRESHOLD_CHARS = get_scan_detection_threshold()
    
    total_chars = 0
    # Check the first few pages for efficiency
    num_pages_to_check = min(len(doc), 3)
    if num_pages_to_check == 0:
        return False

    for i in range(num_pages_to_check):
        page = doc.load_page(i)
        total_chars += len(page.get_text())
    
    avg_chars = total_chars / num_pages_to_check if num_pages_to_check > 0 else 0
    is_scanned = avg_chars < SCAN_DETECTION_THRESHOLD_CHARS
    
    if is_scanned:
        logger.info(f"PDF detected as scanned. Avg chars per page: {avg_chars:.2f} is less than threshold: {SCAN_DETECTION_THRESHOLD_CHARS}")
    return is_scanned

def extract_raw_text_with_pymupdf(file_path: str) -> Tuple[str, bool]:
    """
    Extracts raw text from a PDF using PyMuPDF, optimized for speed.
    
    Returns a tuple containing:
    - The extracted text as a string.
    - A boolean indicating if a fallback to a more robust parser is needed.
      Fallback is triggered for scanned PDFs or if PyMuPDF encounters an error.
    """
    doc = None
    try:
        doc = fitz.open(file_path)
        if is_scanned_pdf(doc):
            return "", True  # Fallback for scanned PDFs
            
        full_text = "".join(page.get_text() for page in doc)
        return full_text, False # Success, no fallback needed
        
    except Exception:
        logger.error(f"Failed to process PDF '{file_path}' with PyMuPDF for raw text extraction. Falling back.", exc_info=True)
        return "", True # Fallback on error
    finally:
        if doc:
            doc.close()