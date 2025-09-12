import os
import requests
from minio import Minio
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import urllib3

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 配置 ---
# 加载 .env 文件中的环境变量
load_dotenv()

# MinIO 配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT_URL", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "documents")

# MongoDB 配置
MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
MONGO_DB_NAME = os.getenv("MONGO_INITDB_DATABASE")
MONGO_COLLECTION_NAME = "files"

# 后端 API 配置
BACKEND_API_URL = "http://localhost:8000/api/v1/embeddings/embed_files"

# 测试文件配置
LOCAL_FILE_PATH = "test_native.pdf"
OBJECT_NAME = f"test_files/{LOCAL_FILE_PATH}"

# --- 初始化客户端 ---
print("--- 初始化客户端 ---")
try:
    # 初始化 MinIO 客户端
    minio_client = Minio(
        MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False  # 在本地开发环境中通常设置为 False
    )
    print("MinIO 客户端初始化成功。")

    # 初始化 MongoDB 客户端
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    print("MongoDB 客户端初始化成功。")

except Exception as e:
    print(f"客户端初始化失败: {e}")
    exit(1)


def main():
    """端到端测试主函数"""
    print("\n--- 开始端到端测试：原生PDF文件处理 ---")

    # 1. 检查本地文件是否存在
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"错误: 测试文件 '{LOCAL_FILE_PATH}' 不在项目根目录中。")
        print("请将测试PDF文件放置在正确位置后重试。")
        return

    # 2. 上传文件到 MinIO
    print(f"\n--- 步骤 1: 上传 '{LOCAL_FILE_PATH}' 到 MinIO Bucket '{MINIO_BUCKET_NAME}' ---")
    try:
        # 检查 bucket 是否存在，不存在则创建
        found = minio_client.bucket_exists(MINIO_BUCKET_NAME)
        if not found:
            minio_client.make_bucket(MINIO_BUCKET_NAME)
            print(f"Bucket '{MINIO_BUCKET_NAME}' 不存在，已创建。")

        minio_client.fput_object(
            MINIO_BUCKET_NAME, OBJECT_NAME, LOCAL_FILE_PATH,
        )
        print(f"文件成功上传为对象: '{OBJECT_NAME}'")
    except Exception as e:
        print(f"文件上传失败: {e}")
        return

    # 3. 在 MongoDB 中创建文件记录
    print(f"\n--- 步骤 2: 在 MongoDB 中创建文件记录 ---")
    try:
        file_doc = {
            "filename": LOCAL_FILE_PATH,
            "object_name": OBJECT_NAME,
            "bucket_name": MINIO_BUCKET_NAME,
            "status": "uploaded",
            "file_type": "pdf", # 预设为 pdf
        }
        result = collection.insert_one(file_doc)
        file_id = str(result.inserted_id)
        print(f"MongoDB 记录创建成功，文件 ID: {file_id}")
    except Exception as e:
        print(f"MongoDB 记录创建失败: {e}")
        # 尝试清理已上传的文件
        try:
            minio_client.remove_object(MINIO_BUCKET_NAME, OBJECT_NAME)
        except Exception as cleanup_e:
            print(f"清理MinIO文件失败: {cleanup_e}")
        return

    # 4. 调用后端 API 触发处理
    print(f"\n--- 步骤 3: 调用后端 API 触发嵌入流程 ---")
    try:
        payload = {
            "file_ids": [file_id]
        }
        headers = {
            "Content-Type": "application/json"
        }
        print(f"发送 POST 请求到: {BACKEND_API_URL}")
        print(f"Payload: {payload}")

        response = requests.post(BACKEND_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # 如果状态码不是 2xx，则抛出异常

        print("API 调用成功!")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        print("\n--- 测试请求已成功发送 ---")
        print("请观察后端服务日志以跟踪处理进度。")
        print("处理完成后，可以运行 verify_milvus.py 脚本来验证结果。")

    except requests.exceptions.RequestException as e:
        print(f"API 调用失败: {e}")
        if e.response:
            print(f"响应状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"触发处理流程时发生未知错误: {e}")


if __name__ == "__main__":
    main()