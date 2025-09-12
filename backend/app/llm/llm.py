import os
import base64
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from ..core.config import settings # Global import

QW_API_KEY = settings.QW_API_KEY
OLLAMA_QWEN_VL_MAX_LATEST = settings.OLLAMA_QWEN_VL_MAX_LATEST

# Ollama Configuration
OLLAMA_URL = settings.OLLAMA_SERVING_URL # Use the specific serving URL
OLLAMA_CHAT_MODEL = settings.OLLAMA_CHAT_MODEL # Use the chat model from COT_MODE
OLLAMA_COT_MODEL = settings.OLLAMA_COT_MODEL # Corrected variable name
OLLAMA_QWEN_MODEL = settings.OLLAMA_QWEN_MODEL # Added Qwen model for Ollama

def get_llm(show_think_process: bool = False) -> ChatOllama:
    """
    LLM factory function.
    Returns a ChatOllama instance based on the 'show_think_process' flag.
    - If True, uses the Chain-of-Thought model (OLLAMA_COT_MODEL).
    - If False, uses the standard chat model (OLLAMA_CHAT_MODEL).
    """
    if not OLLAMA_URL:
        # logger.error("OLLAMA_SERVING_URL is not set in the environment variables.")
        raise ValueError("OLLAMA_SERVING_URL must be set to a valid Ollama server URL.")

    if show_think_process:
        model_name = OLLAMA_COT_MODEL
        # logger.info(f"Using COT model: {model_name} at {OLLAMA_URL}")
    else:
        model_name = OLLAMA_CHAT_MODEL
        # logger.info(f"Using Chat model: {model_name} at {OLLAMA_URL}")
    
    # Robustly clean up the base URL to prevent issues with duplicate /api paths
    cleaned_base_url = OLLAMA_URL.rstrip("/")
    if cleaned_base_url.endswith("/api"):
        cleaned_base_url = cleaned_base_url[:-4]
    cleaned_base_url = cleaned_base_url.rstrip("/")

    return ChatOllama(model=model_name, base_url=cleaned_base_url)

# The global llm instance is now deprecated. Code should use the get_llm() factory.
# llm = ChatOpenAI(...)

async def llm_qwen_vl_max_ainvoke(message:str,url,model:str=OLLAMA_QWEN_VL_MAX_LATEST):
    client = OpenAI(
        api_key=QW_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model=model,
        # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "# backend\n根据用户的问题，总结图片的内容分，并将其输入到后续的智能体中进行回答。\n# task\n您的任务，是根据问题总结图片中对问题有帮助的关键信息,请你以JSON格式输出，不要输出```json```代码段”"}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":url
                        },
                    },

                    {"type": "text", "text": message},
                ],
            },
        ],
    )
    print(completion)
    summarize_content = completion.choices[0].message.content.replace('"',"'").replace("\n","").replace(" ","").replace("{","").replace("}","")
    return summarize_content

async def llm_ollama_deepseek_ainvoke(message: str, model: str = OLLAMA_COT_MODEL, base_url: str = settings.OLLAMA_SERVING_URL) -> str:
    """
    使用本地Ollama模型(deepseek-r1:8b)异步生成文本响应

    Args:
        message: 用户输入的消息
        model: Ollama模型名称 (默认为 deepseek-r1:8b, 可通过环境变量 OLLAMA_COT_MODEL 配置)
        base_url: Ollama服务的URL (默认为 http://localhost:11434, 可通过环境变量 OLLAMA_URL 配置)

    Returns:
        生成的文本响应
    """
    try:
        # client = OpenAI(
        #     base_url=OLLAMA_URL,  # Ollama expects the base URL without /api/
        #     # required but ignored
        #     api_key='ollama',
        #     model=model
        # )
        # Robustly clean up the base URL to prevent issues with duplicate /api paths
        cleaned_base_url = base_url.rstrip("/")
        if cleaned_base_url.endswith("/api"):
            cleaned_base_url = cleaned_base_url[:-4]
        cleaned_base_url = cleaned_base_url.rstrip("/")
        ollama_llm = ChatOllama(model=model, base_url=cleaned_base_url)
        # response = await client.chat.completions.create(
        #     messages=message
        #     )
        response = await ollama_llm.ainvoke(message)
        return response.content
    except Exception as e:
        print(f"Error calling Ollama model {model}: {e}")
        return f"Error generating response from Ollama: {e}"

async def llm_ollama_qwen_ainvoke(message: str, model: str = OLLAMA_QWEN_MODEL, base_url: str = settings.OLLAMA_SERVING_URL) -> str:
    """
    使用本地Ollama模型(qwen2:7b)异步生成文本响应，支持function calling。

    Args:
        message: 用户输入的消息
        model: Ollama模型名称 (默认为 qwen2:7b, 可通过环境变量 OLLAMA_QWEN_MODEL 配置)
        base_url: Ollama服务的URL (默认为 http://localhost:11434, 可通过环境变量 OLLAMA_URL 配置)

    Returns:
        生成的文本响应
    """
    try:
        # Robustly clean up the base URL to prevent issues with duplicate /api paths
        cleaned_base_url = base_url.rstrip("/")
        if cleaned_base_url.endswith("/api"):
            cleaned_base_url = cleaned_base_url[:-4]
        cleaned_base_url = cleaned_base_url.rstrip("/")
        ollama_llm = ChatOllama(model=model, base_url=cleaned_base_url)
        # For function calling, you would typically pass tools to the LLM
        # For now, we'll just return content, and the agent will handle parsing.
        response = await ollama_llm.ainvoke(message)
        return response.content
    except Exception as e:
        print(f"Error calling Ollama Qwen model {model}: {e}")
        return f"Error generating response from Ollama Qwen: {e}"

async def llm_ollama_vision_ainvoke(question: str, image_bytes: bytes, model: str = settings.OLLAMA_QWEN_VL_MAX_LATEST) -> str:
    """
    使用本地Ollama视觉模型异步处理图片并生成文本响应。

    Args:
        question: 用户关于图片的问题。
        image_bytes: 图片文件的字节内容。
        model: Ollama视觉模型的名称。

    Returns:
        生成的文本响应。
    """
    try:
        # 将图片字节编码为Base64字符串
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{base64_image}"

        # 获取Ollama实例
        cleaned_base_url = settings.OLLAMA_SERVING_URL.rstrip("/")
        if cleaned_base_url.endswith("/api"):
            cleaned_base_url = cleaned_base_url[:-4]
        cleaned_base_url = cleaned_base_url.rstrip("/")
        
        llm = ChatOllama(model=model, base_url=cleaned_base_url)

        # 构建多模态消息
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": question,
                },
                {
                    "type": "image_url",
                    "image_url": image_url,
                },
            ]
        )

        # 调用模型并获取响应
        response = await llm.ainvoke([message])
        return response.content

    except Exception as e:
        print(f"Error calling Ollama vision model {model}: {e}")
        return f"Error generating response from Ollama Vision: {e}"