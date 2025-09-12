docker run --gpus all \
  --shm-size 32g \
  -p 30000:30000 \
  --ipc=host \
  mineru-sglang:latest \
  mineru-sglang-server --host 0.0.0.0 --port 30000