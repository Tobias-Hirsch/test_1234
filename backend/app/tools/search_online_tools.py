import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from msrest.authentication import CognitiveServicesCredentials
import os
from ..core.config import settings  # Global import for configuration settings  

# Replace with your Bing Search V7 subscription key and endpoint
# You should store this in environment variables or a configuration file
BING_SEARCH_KEY = settings.BING_SEARCH_KEY
BING_SEARCH_ENDPOINT = settings.BING_SEARCH_ENDPOINT

async def bingsearch(queries: List[str], max_results: int = 10) -> Dict[str, List[Any]]:
    """
    异步处理多个Bing搜索查询

    Args:
        queries: 包含多个搜索问题的数组
        max_results: 每个查询的最大结果数量

    Returns:
        字典，键为查询字符串，值为对应的搜索结果列表
    """
    results = {}

    if not BING_SEARCH_KEY or BING_SEARCH_KEY == "YOUR_BING_SEARCH_KEY":
        print("Bing Search API key not configured.")
        return {query: [] for query in queries}

    if not BING_SEARCH_ENDPOINT or BING_SEARCH_ENDPOINT == "YOUR_BING_SEARCH_ENDPOINT":
         print("Bing Search API endpoint not configured.")
         return {query: [] for query in queries}


    client = WebSearchClient(endpoint=BING_SEARCH_ENDPOINT, credentials=CognitiveServicesCredentials(BING_SEARCH_KEY))

    async def search_single_query(query: str) -> List[Any]:
        try:
            # Perform the search
            web_data = client.web.search(query=query, count=max_results, safe_search=SafeSearch.strict)

            # Process and return results
            bing_results = []
            if web_data.web_pages and web_data.web_pages.value:
                for item in web_data.web_pages.value:
                    bing_results.append({
                        "title": item.name,
                        "href": item.url,
                        "body": item.snippet
                    })
            return bing_results
        except Exception as e:
            print(f"Bing search for query '{query}' failed: {e}")
            return [] # Return empty list on failure

    # Process queries concurrently
    tasks = [search_single_query(query) for query in queries]
    all_results = await asyncio.gather(*tasks)

    # Associate results with queries
    for query, result in zip(queries, all_results):
        results[query] = result

    return results

async def duckduckgosearch(queries: List[str], max_results: int = 10, max_retries: int = 3, retry_delay: float = 2.0) -> \
Dict[str, List[Any]]:
    """
    异步处理多个DuckDuckGo搜索查询

    Args:
        queries: 包含多个搜索问题的数组
        max_results: 每个查询的最大结果数量
        max_retries: 遇到限流时的最大重试次数
        retry_delay: 重试之间的基础延迟时间(秒)

    Returns:
        字典，键为查询字符串，值为对应的搜索结果列表
    """
    results = {}

    async def search_single_query(query: str) -> List[Any]:
        loop = asyncio.get_event_loop()

        for attempt in range(max_retries):
            try:
                with ThreadPoolExecutor() as executor:
                    return await loop.run_in_executor(
                        executor,
                        lambda: list(DDGS().text(query, max_results=max_results))
                    )
            except DuckDuckGoSearchException as e:
                if "Ratelimit" in str(e) and attempt < max_retries - 1:
                    # 添加随机抖动以避免所有请求同时重试
                    jitter = random.uniform(0.3, 0.5)
                    wait_time = retry_delay * (2 ** attempt) * jitter
                    print(f"查询 '{query}' 遇到限流，等待 {wait_time:.2f} 秒后重试 ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"查询 '{query}' 失败: {e}")
                    return []  # 返回空列表表示查询失败

        return []  # 所有重试都失败

    # 为了避免同时发送太多请求，分批处理查询
    batch_size = 2  # 每批处理的查询数量
    all_results = []

    for i in range(0, len(queries), batch_size):
        batch_queries = queries[i:i + batch_size]

        # 创建当前批次的查询任务
        tasks = [search_single_query(query) for query in batch_queries]

        # 等待当前批次完成
        batch_results = await asyncio.gather(*tasks)
        all_results.extend(batch_results)

        # 批次之间添加延迟
        if i + batch_size < len(queries):
            await asyncio.sleep(1.0)  # 批次之间等待1秒

    # 将结果与查询关联
    for query, result in zip(queries, all_results):
        results[query] = result

    return results
