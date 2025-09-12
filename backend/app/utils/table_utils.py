import logging
from bs4 import BeautifulSoup
from typing import List

logger = logging.getLogger(__name__)

def linearize_html_table_to_markdown(html_content: str) -> str:
    """
    将包含单个 HTML 表格的字符串转换为 Markdown 格式。

    :param html_content: 包含 <table> 标签的 HTML 字符串。
    :return: Markdown 格式的表格字符串。
    """
    try:
        # 使用 lxml 作为解析器，如果不可用，BeautifulSoup 会回退到 html.parser
        soup = BeautifulSoup(html_content, 'lxml')
        table = soup.find('table')
        if not table:
            logger.warning("在提供的 HTML 内容中未找到 <table> 标签。")
            return ""

        markdown_rows = []
        
        # --- 处理表头 (thead) ---
        header = table.find('thead')
        header_cols = []
        if header:
            header_row = header.find('tr')
            if header_row:
                header_cols = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                markdown_rows.append("| " + " | ".join(header_cols) + " |")
                markdown_rows.append("|" + "---|" * len(header_cols))

        # --- 处理表体 (tbody) ---
        body = table.find('tbody')
        if not body:
            # 如果没有 tbody，直接在 table 中找 tr
            body = table
        
        first_row_is_header = False
        if not header and body.find('tr'):
            # 如果没有 thead，检查第一行是否像表头（全都是 th 或粗体）
            first_row = body.find('tr')
            if all(cell.name == 'th' for cell in first_row.find_all(['th', 'td'])):
                 first_row_is_header = True

        for i, row in enumerate(body.find_all('tr')):
            # 如果没有 thead，将第一行作为表头
            if not header and i == 0 and not header_cols:
                header_cols = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
                markdown_rows.append("| " + " | ".join(header_cols) + " |")
                markdown_rows.append("|" + "---|" * len(header_cols))
                if first_row_is_header:
                    continue

            # 跳过 thead 中的行，因为它已经被处理过了
            if row.parent.name == 'thead':
                continue

            cols = [td.get_text(strip=True).replace('\n', ' ') for td in row.find_all('td')]
            if cols:
                markdown_rows.append("| " + " | ".join(cols) + " |")
            
        # 如果在 thead 和 tbody 中都没有找到行，则尝试将 table 的第一行作为表头
        if not markdown_rows and table.find_all('tr'):
            all_rows = table.find_all('tr')
            header_cols = [cell.get_text(strip=True) for cell in all_rows[0].find_all(['th', 'td'])]
            markdown_rows.append("| " + " | ".join(header_cols) + " |")
            markdown_rows.append("|" + "---|" * len(header_cols))
            for row in all_rows[1:]:
                cols = [td.get_text(strip=True).replace('\n', ' ') for td in row.find_all('td')]
                markdown_rows.append("| " + " | ".join(cols) + " |")


        return "\n".join(markdown_rows)

    except ImportError:
        logger.error("缺少 'beautifulsoup4' 或 'lxml' 依赖。请运行 'pip install beautifulsoup4 lxml'。")
        # 返回原始 HTML 作为后备
        return f"<html_table>\n{html_content}\n</html_table>"
    except Exception as e:
        logger.error(f"解析 HTML 表格时出错: {e}")
        # 返回原始 HTML 作为后备
        return f"<html_table>\n{html_content}\n</html_table>"
