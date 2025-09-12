import re
from typing import List
import asyncio
from ..core.config import settings  # Global import for configuration settings

AI_TEMPLATE_SEGMENT_SPLIT_MAX_SIZE = int(settings.AI_TEMPLATE_SEGMENT_SPLIT_MAX_SIZE)

async def semantic_text_splitter(text: str, max_length: int = 2000) -> List[str]:
    """
    异步语义文本分割器，将长文本分割成较小的段落。

    参数:
        text (str): 需要切分的文本
        max_length (int): 每段的最大字符数，默认为2000

    返回:
        list: 切分后的文本段落列表
    """
    # 如果文本长度小于最大长度，直接返回
    if len(text) <= max_length:
        return [text]

    # 初始化结果列表和当前段落
    segments = []
    current_segment = ""

    # 按段落切分
    paragraphs = re.split(r'\n\s*\n', text)

    # 处理大型段落的任务列表
    tasks = []

    for paragraph in paragraphs:
        # 如果段落本身超过最大长度，需要进一步异步处理
        if len(paragraph) > max_length:
            # 将长段落的处理添加到任务列表
            tasks.append(_process_long_paragraph(paragraph, max_length))
        else:
            # 检查添加当前段落是否会超过最大长度
            if len(current_segment) + len(paragraph) + 2 <= max_length:  # +2 for newline
                if current_segment:
                    current_segment += "\n\n" + paragraph
                else:
                    current_segment = paragraph
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = paragraph

    # 异步处理所有长段落
    if tasks:
        long_paragraph_results = await asyncio.gather(*tasks)
        # 将处理结果扁平化添加到segments
        for result in long_paragraph_results:
            segments.extend(result)

    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment.strip())

    return segments


async def _process_long_paragraph(paragraph: str, max_length: int) -> List[str]:
    """
    异步处理长段落，将其分割成更小的部分。

    参数:
        paragraph (str): 需要处理的长段落
        max_length (int): 每段的最大字符数

    返回:
        list: 分割后的段落列表
    """
    segments = []
    current_segment = ""

    # 针对中文和英文的常见句子结束符
    sentence_endings = r'([。！？\.\!\?][\"\'\'\"]?)'
    paragraph_sentences = re.split(sentence_endings, paragraph)

    # 重组句子（因为split会分离标点符号）
    sentences = []
    i = 0
    while i < len(paragraph_sentences):
        if i + 1 < len(paragraph_sentences) and re.match(sentence_endings, paragraph_sentences[i + 1]):
            sentences.append(paragraph_sentences[i] + paragraph_sentences[i + 1])
            i += 2
        else:
            if paragraph_sentences[i].strip():
                sentences.append(paragraph_sentences[i])
            i += 1

    for sentence in sentences:
        # 如果单个句子超过最大长度，按标点符号切分
        if len(sentence) > max_length:
            await _process_long_sentence(sentence, max_length, segments)
        else:
            # 检查添加当前句子是否会超过最大长度
            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence

    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment.strip())

    return segments


async def _process_long_sentence(sentence: str, max_length: int, segments: List[str]) -> None:
    """
    处理超长句子，将其分割并添加到segments列表中。

    参数:
        sentence (str): 需要处理的长句子
        max_length (int): 每段的最大字符数
        segments (List[str]): 存储结果的列表
    """
    current_segment = ""
    punctuation_splits = re.split(r'([,;，；、])', sentence)
    i = 0
    while i < len(punctuation_splits):
        part = punctuation_splits[i]
        # 如果有标点符号，添加到部分中
        if i + 1 < len(punctuation_splits) and len(punctuation_splits[i + 1]) == 1:
            part += punctuation_splits[i + 1]
            i += 2
        else:
            i += 1

        if len(current_segment) + len(part) <= max_length:
            current_segment += part
        else:
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = part

    # 添加最后一个部分
    if current_segment:
        segments.append(current_segment.strip())