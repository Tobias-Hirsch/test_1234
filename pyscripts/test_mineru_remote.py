import os
import argparse
from pathlib import Path
from loguru import logger

# 捕获导入错误，以便提供更清晰的指引
try:
    # 核心函数，基于官方 demo.py 的实现
    from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
    from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
    from mineru.utils.enum_class import MakeMode
    from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2
except ImportError as e:
    logger.error(f"无法导入 MinerU 组件: {e}")
    logger.error("请确认 'mineru[core]' 已在当前 Python 环境中正确安装。")
    exit(1)


def test_remote_mineru(file_path: str, remote_url: str="http://1.116.119.85:8908"):
    """
    使用 MinerU 的 VLM 后端函数，通过远程 sglang 服务解析 PDF。
    此方法严格遵循官方 demo.py 脚本的调用逻辑。
    """
    if not os.path.exists(file_path):
        logger.error(f"文件未找到: '{file_path}'")
        return

    logger.info(f"正在读取文件: {file_path}")
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    # MinerU 内部流程通常会进行此转换
    pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes)

    logger.info(f"正在连接到远程 MinerU sglang 服务: {remote_url}")

    try:
        # 1. 调用 VLM 分析函数，该函数将请求发送到 sglang 服务
        middle_json, _ = vlm_doc_analyze(
            pdf_bytes,
            image_writer=None,  # 本次测试不保存图片
            backend="sglang-client",
            server_url=remote_url
        )

        # 2. 从返回结果中提取核心的 pdf_info 结构
        pdf_info = middle_json.get("pdf_info")
        if not pdf_info:
            logger.error("解析失败: 未在结果中找到 'pdf_info'。")
            return

        # 3. 从解析结构中生成 Markdown
        logger.info("正在从解析结果生成 Markdown...")
        md_content = vlm_union_make(
            pdf_info,
            make_mode=MakeMode.MM_MD
        )

        print("\n" + "="*20 + " 解析结果 " + "="*20 + "\n")
        print(md_content)
        print("\n" + "="*20 + " 结果结束 " + "="*20 + "\n")

        # 4. 将结果保存到文件以便详细检查
        output_filename = f"{Path(file_path).stem}_result.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.success(f"结果已成功保存到: {output_filename}")

    except Exception as e:
        logger.exception(f"远程解析过程中发生错误: {e}")
        logger.error("请检查：")
        logger.error("1. 远程 sglang 服务是否正在运行且可访问。")
        logger.error(f"2. URL '{remote_url}' 是否正确。")
        logger.error("3. `mineru[core]` 包是否已正确安装。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="基于官方 demo.py 的 MinerU sglang 远程测试脚本。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file_path", type=str, help="需要解析的本地 PDF 文件路径。")
    parser.add_argument(
        "-u", "--url",
        type=str,
        required=True,
        help="远程 sglang 服务的 URL (例如: http://your-domain.com:7861)"
    )

    args = parser.parse_args()
    test_remote_mineru(args.file_path, args.url)