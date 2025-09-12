import os
import matplotlib
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 强制设置 Milvus 环境变量
os.environ['MILVUS_HOST'] = '127.0.0.1'
#'10.32.7.109'
os.environ['MILVUS_PORT'] = '19530'

# 在导入 pyplot 之前设置后端
os.environ['MPLBACKEND'] = 'Agg'
matplotlib.use('Agg', force=True)

# 禁用交互模式
matplotlib.interactive(False)

# 其他可能需要的环境变量
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

print("Environment initialized successfully")
print(f"Milvus Host: {os.getenv('MILVUS_HOST')}")
print(f"Milvus Port: {os.getenv('MILVUS_PORT')}") 