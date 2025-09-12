import asyncio
import logging
from app.services.mineru_service import mineru_client

# --- 配置日志记录 ---
# 这将使得日志输出更加清晰
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    一个演示如何使用 MinerUClient 处理 MinIO 中文件的示例函数。
    """
    logger.info("--- 开始演示 MinerU 服务调用 ---")

    # 1. 定义要处理的文件在 MinIO 中的路径。
    #    格式通常是 "bucket_name/path/to/your/file.pdf"
    #    请根据你的实际情况修改这个示例路径。
    document_to_process = "your-bucket-name/your-document-path.pdf"
    logger.info(f"目标文件: {document_to_process}")

    # 2. 调用我们统一的 MinerU 客户端。
    #    客户端会自动从 settings 中读取 API 地址。
    result = await mineru_client.process_document(document_path=document_to_process)

    # 3. 处理返回结果。
    if result:
        logger.info("成功从 MinerU 服务获取响应。")
        # 打印部分结果以供演示。
        # 注意：你需要根据 MinerU API 的实际返回结构来解析这里的 'data'。
        processed_data = result.get("data", {})
        content_preview = str(processed_data)[:500] # 打印结果的前500个字符
        logger.info(f"处理结果预览: {content_preview}...")
    else:
        logger.error("调用 MinerU 服务失败。请检查服务日志和网络连接。")

    logger.info("--- 演示结束 ---")


if __name__ == "__main__":
    # 要运行这个脚本，请确保你的 .env 文件已经配置了正确的 MINERU_API_URL。
    # 然后在 backend 目录下，激活环境并运行：
    # python -m app.modules.magicpdf_minio
    asyncio.run(main())
