import os
import logging
from typing import Tuple, Optional
import fitz  # PyMuPDF
from ..core.config import settings
from app.services.mineru_unified_service import get_unified_mineru_processor

# --- 配置日志记录 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# --- 更新的 MinerU 处理器调用 ---
async def process_pdf_with_mineru(file_bytes: bytes, filename: str) -> Optional[dict]:
    """
    通过配置的 MinerU 处理器（本地或远程）来处理 PDF 的统一入口点。
    现在会根据 settings 传递处理策略。

    :param file_bytes: PDF 文件的字节内容。
    :param filename: 原始文件名，用于日志记录。
    :return: MinerU 服务返回的 JSON 响应，如果失败则返回 None。
    """
    strategy = settings.PDF_PROCESSING_STRATEGY
    logger.info(f"使用 MinerU 处理器处理文档: {filename}，策略: {strategy}")
    
    # 使用统一处理器获取单例处理器
    processor = get_unified_mineru_processor()
    
    # 调用统一的接口，并传递处理策略
    result = await processor.process_document_bytes(file_bytes, filename, strategy=strategy)
    
    if not result:
        logger.error(f"使用 MinerU 处理器处理文档失败: {filename} (策略: {strategy})")
        return None
    return result


# --- 通用的文件和 PDF 辅助函数 ---

def read_all_files(folder_path: str) -> list:
    """读取指定文件夹下的所有文件名。"""
    files_list = []
    if not os.path.exists(folder_path):
        logger.warning(f"文件夹 {folder_path} 不存在。")
        return files_list
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            files_list.append(filename)
    return files_list


def fix_pdf(file_path: str) -> Optional[str]:
    """
    尝试使用 PyMuPDF 修复损坏的 PDF 文件。

    :param file_path: PDF 文件的完整路径。
    :return: 修复后的文件路径，如果修复失败则返回 None。
    """
    doc = None  # 初始化为 None
    try:
        doc = fitz.open(file_path)
        fixed_file_path = file_path.replace(".pdf", ".fixed.pdf")
        doc.save(fixed_file_path)
        logger.info(f"PDF 文件修复成功: {file_path} -> {fixed_file_path}")
        return fixed_file_path
    except Exception as e:
        logger.error(f"PDF 修复失败 {file_path}: {e}")
        return None
    finally:
        if doc:
            doc.close()


def check_pdf_integrity(file_path: str) -> bool:
    """使用 PyMuPDF 检查 PDF 文件的基本完整性。"""
    try:
        doc = fitz.open(file_path)
        # 检查文件是否能被打开并且至少有一页
        is_ok = doc.is_pdf and doc.page_count > 0
        doc.close()
        return is_ok
    except Exception as e:
        logger.error(f"PDF 完整性检查失败 for {file_path}: {e}")
        return False


def extract_raw_text_with_pymupdf(file_path: str) -> Tuple[str, int]:
    """
    使用 PyMuPDF 从 PDF 文件中提取原始文本。

    :param file_path: PDF 文件的路径。
    :return: 一个包含提取的文本和总页数的元组。
    """
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        page_count = doc.page_count
        doc.close()
        logger.info(f"成功从 {file_path} 提取文本, 页数: {page_count}")
        return text, page_count
    except Exception as e:
        logger.error(f"使用 PyMuPDF 从 PDF {file_path} 提取文本时出错: {e}")
        return "", 0

