import os
from typing import List
from ..core.config import settings # Global import
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.llm.llm import get_llm
from pydantic import BaseModel, Field


QW_API_KEY = settings.QW_API_KEY

class SummarizedDoc(BaseModel):
    summarize: str = Field(description="总结摘要")
class SummarizedDocKeyWord(BaseModel):
    key_word: List[str] = Field(description="关键词")

# Prompt templates remain global
prompt_summarize_doc = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
# Backend
    您是工业领域的专家，为了方便用户选取想要使用的文献，现在需要对文献生成总结，总结的越精练越好。

# Task
    您的任务是以一个专业的专家角度，根据标题和正文总结这篇文章，形成一个摘要，这个摘要尽可能简短，但是必须包含使用层面的必要信息
            """,
        ),
        ("placeholder", "{title}"),
        ("placeholder", "{content}"),
    ]
)


prompt_summarize_doc_key_word = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
# Backend
    您是法律领域的专家，因为广大民众需要普法，为了方便民众选取想要阅读的法律，现在需要对法律文献总结生成关键词

# Task
    您的任务是以一个专业的法学律师角度，根据标题和正文总结这篇法律文章，形成多个关键词，这些关键词里必须准确包含整个法律的所有关键信息以及所有涉及的领域，尽可能完善且避开敏感词，但是关键词不应该太多，要保持在5个到150个之间
            """,
        ),
        ("placeholder", "{title}"),
        ("placeholder", "{content}"),
    ]
)

# Chains are now constructed inside the functions to use the correct LLM instance.

async def fn_async_summarize_doc(title,content):
    llm_instance = get_llm(show_think_process=False)
    chain = prompt_summarize_doc | llm_instance.with_structured_output(SummarizedDoc).with_retry(stop_after_attempt=3)
    summarize_doc = await chain.ainvoke({"title": [("user", title)], "content": [("user", content)]},
            config={"run_name": f"chain_summarize_doc_{title}"})
    return summarize_doc

def fn_summarize_doc(title,content):
    llm_instance = get_llm(show_think_process=False)
    chain = prompt_summarize_doc | llm_instance.with_structured_output(SummarizedDoc).with_retry(stop_after_attempt=3)
    summarize_doc = chain.invoke({"title": [("user", title)], "content": [("user", content)]},
            config={"run_name": f"chain_summarize_doc_{title}"})
    return summarize_doc

async def fn_async_summarize_doc_key_word(title,content):
    llm_instance = get_llm(show_think_process=False)
    chain = prompt_summarize_doc_key_word | llm_instance.with_structured_output(SummarizedDocKeyWord).with_retry(stop_after_attempt=3)
    summarize_doc_key_word = await chain.ainvoke({"title": [("user", title)], "content": [("user", content)]},
            config={"run_name": f"chain_summarize_doc_key_word_{title}"})
    return summarize_doc_key_word

def fn_summarize_doc_key_word(title,content):
    llm_instance = get_llm(show_think_process=False)
    chain = prompt_summarize_doc_key_word | llm_instance.with_structured_output(SummarizedDocKeyWord).with_retry(stop_after_attempt=3)
    summarize_doc_key_word = chain.invoke({"title": [("user", title)], "content": [("user", content)]},
            config={"run_name": f"chain_summarize_doc_key_word_{title}"})
    return summarize_doc_key_word

