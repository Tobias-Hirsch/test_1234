import json
import logging
from typing import AsyncGenerator, Any, Dict

logger = logging.getLogger(__name__)

async def sse_stream_formatter(generator: AsyncGenerator[Dict[str, Any], None]) -> AsyncGenerator[str, None]:
    """
    Formats the output of an asynchronous generator into Server-Sent Events (SSE).
    It expects the generator to yield dictionaries with 'event' and 'data' keys.
    """
    try:
        async for chunk in generator:
            if isinstance(chunk, dict) and 'event' in chunk and 'data' in chunk:
                event = chunk['event']
                data = chunk['data']
                
                # ALWAYS JSON-encode the data part to handle special characters and ensure consistency
                data_str = json.dumps(data)
                
                yield f"event: {event}\ndata: {data_str}\n\n"
            else:
                logger.warning(f"sse_stream_formatter received chunk of unexpected format: {chunk}")

    except Exception as e:
        logger.error(f"Error in sse_stream_formatter: {e}", exc_info=True)
        error_data = json.dumps({'error': str(e)})
        yield f"event: error\ndata: {error_data}\n\n"