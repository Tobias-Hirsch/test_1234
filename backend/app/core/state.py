import asyncio

# A global lock to ensure that document processing is done one at a time.
# This prevents resource contention, especially when using the local 'pipeline'
# backend for MinerU, which can be CPU/memory intensive.
doc_processing_lock = asyncio.Lock()