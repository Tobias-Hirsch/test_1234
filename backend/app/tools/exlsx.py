# Developer: Jinglu Han
# mailbox: admin@de-manufacturing.cn

import aiohttp
import pandas as pd
import io
import asyncio
from typing import Dict, List, Any, Union
from app.services.logging import xlsx_process_content_logger as logger


async def download_and_parse_xlsx(url) -> \
Union[Dict[str, pd.DataFrame], None]:
    """
    从指定URL异步下载xlsx文件并解析其内容

    Args:
        url: xlsx文件的下载地址

    Returns:
        包含所有工作表数据的字典，键为工作表名称，值为DataFrame
        如果下载或解析失败则返回None
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"下载失败，状态码: {response.status}")
                    return None

                # 读取响应内容
                logger.info("读取响应内容")
                content = await response.read()

                # 使用pandas读取Excel内容
                logger.info("使用pandas读取Excel内容")
                excel_data = {}
                with io.BytesIO(content) as file_obj:
                    # 读取所有工作表，明确指定使用openpyxl引擎
                    excel_file = pd.ExcelFile(file_obj, engine='openpyxl')
                    sheet_names = excel_file.sheet_names

                    for sheet_name in sheet_names:
                        df = excel_file.parse(sheet_name)
                        excel_data[sheet_name] = df
                result :str  = ''
                for sheet_name, df in excel_data.items():
                    result += f"工作表: {sheet_name}\n"
                    result += df.to_string()
                    result += "\n"
                    result += '-' * 50
                    result += "\n"
                return result
    except Exception as e:
        logger.error(f"处理Excel文件时出错: {str(e)}")
        return None

async def extract_excel_content_from_file(file_path: str) -> Union[str, None]:
    """
    从本地xlsx文件解析其内容并返回字符串格式。

    Args:
        file_path: 本地xlsx文件的路径。

    Returns:
        包含所有工作表数据的字符串，如果解析失败则返回None。
    """
    try:
        logger.info(f"从本地文件解析Excel内容: {file_path}")
        excel_data = {}
        # Use pandas to read the Excel file directly from the local path
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = excel_file.sheet_names

        for sheet_name in sheet_names:
            df = excel_file.parse(sheet_name)
            excel_data[sheet_name] = df

        result: str = ''
        for sheet_name, df in excel_data.items():
            result += f"工作表: {sheet_name}\n"
            result += df.to_string()
            result += "\n"
            result += '-' * 50
            result += "\n"
        logger.info(f"成功从文件 {file_path} 提取Excel内容")
        return result
    except Exception as e:
        logger.error(f"处理本地Excel文件时出错: {str(e)}")
        return None

async def extract_excel_content_from_bytes(file_content: bytes, filename: str = None) -> Union[str, None]:
    """
    从Excel文件的字节流中解析其内容并返回字符串格式。

    Args:
        file_content: Excel文件的字节内容。
        filename: 文件名，用于确定文件格式。

    Returns:
        包含所有工作表数据的字符串，如果解析失败则返回None。
    """
    try:
        logger.info("从字节流解析Excel内容...")
        
        # 根据文件扩展名选择合适的引擎
        engine = 'openpyxl'  # 默认引擎，用于.xlsx文件
        if filename:
            file_ext = filename.lower().split('.')[-1]
            if file_ext == 'xls':
                engine = 'xlrd'
                logger.info("检测到.xls格式，使用xlrd引擎")
            else:
                logger.info("检测到.xlsx格式，使用openpyxl引擎")
        
        excel_data = {}
        with io.BytesIO(file_content) as file_obj:
            try:
                # 尝试使用指定的引擎
                excel_file = pd.ExcelFile(file_obj, engine=engine)
                sheet_names = excel_file.sheet_names

                for sheet_name in sheet_names:
                    df = excel_file.parse(sheet_name)
                    excel_data[sheet_name] = df
                    
            except Exception as engine_error:
                logger.warning(f"使用{engine}引擎失败: {engine_error}，尝试自动检测...")
                # 如果指定引擎失败，尝试自动检测
                file_obj.seek(0)  # 重置文件指针
                excel_file = pd.ExcelFile(file_obj)  # 让pandas自动选择引擎
                sheet_names = excel_file.sheet_names

                for sheet_name in sheet_names:
                    df = excel_file.parse(sheet_name)
                    excel_data[sheet_name] = df

        result: str = ''
        for sheet_name, df in excel_data.items():
            result += f"工作表: {sheet_name}\n"
            result += df.to_string()
            result += "\n"
            result += '-' * 50
            result += "\n"
        
        logger.info(f"成功从字节流中提取Excel内容，共{len(excel_data)}个工作表")
        return result
    except Exception as e:
        logger.error(f"从字节流处理Excel文件时出错: {str(e)}")
        return None

# 使用示例
async def main():
    result = await download_and_parse_xlsx('http://localhost:9001/api/v1/download-shared-object/aHR0cDovLzEyNy4wLjAuMTo5MDAwL21tLXJhZy1idWNrZXQvcm9zdGkvQVdJX0ZMNDFBU1MwMDAyLXh4LUJfQTEueGxzeD9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPTI5NFlTOUlEWVVGNjYxVExBV0NNJTJGMjAyNTA1MjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNTI2VDE0MjYyOFomWC1BbXotRXhwaXJlcz00MzIwMCZYLUFtei1TZWN1cml0eS1Ub2tlbj1leUpoYkdjaU9pSklVelV4TWlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaFkyTmxjM05MWlhraU9pSXlPVFJaVXpsSlJGbFZSalkyTVZSTVFWZERUU0lzSW1WNGNDSTZNVGMwT0RNeE1EZ3hOQ3dpY0dGeVpXNTBJam9pYldsdWFXOWhaRzFwYmlKOS5VeGtZY05jRUxtTmp5aUNPNWgwdFc4Sy1KTUVOaWwxTzQ1dUp3YXc4TmRxRWkzWTlISDFGdHVrUXROdFlheGpYdHhHUERWOGJkZHh5RDNaZ1VCMWQtQSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmdmVyc2lvbklkPW51bGwmWC1BbXotU2lnbmF0dXJlPWUzYWIxMzgxN2Q4MWY1ZTk3ZjA3MjFjZTczYTY0ZGJhOThmYWRhNTZlMWYyMjRhNzViODY2NTYxMWFkZjc1NDg')
    if result:
        for sheet_name, df in result.items():
            print(f"工作表: {sheet_name}")
            print(df.head())
            print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())