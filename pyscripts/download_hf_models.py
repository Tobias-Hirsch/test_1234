import os
os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'

from huggingface_hub import disable_ssl_verify
disable_ssl_verify()

from sentence_transformers import SentenceTransformer

model_name = 'BAAI/bge-reranker-large'
local_model_path = './models/bge-reranker-large' # 你可以指定任何你想要的本地路径

print(f"Downloading model '{model_name}' to '{local_model_path}'...")

# 这会自动下载模型文件到指定的路径
model = SentenceTransformer(model_name)
model.save(local_model_path)

print("Model downloaded and saved successfully.")
