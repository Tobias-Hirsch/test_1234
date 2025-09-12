import json
from typing import Any, Dict, Optional
from .base_agent import BaseAgent
from app.llm.llm import llm_ollama_deepseek_ainvoke
from app.services import auth
from fastapi import HTTPException

class SearchAgent(BaseAgent):
    """
    The Search Agent performs web searches or searches within specified
    internal databases to gather external information relevant to the user's query.
    """

    def __init__(self):
        super().__init__(name="Search Agent",
                         description="Performs web searches and gathers external information.")

    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a search query to retrieve and summarize external information using DeepSeek,
        with integrated permission checks.

        Args:
            task (str): The specific search query.
            context (Dict[str, Any]): Contextual information, e.g., user prompt.

        Returns:
            Dict[str, Any]: A dictionary containing the search results and thoughts.
        """
        thoughts = []
        output = {}
        query = context.get("query", task)
        db_session = context.get("db_session")
        current_user = context.get("current_user")

        # Permission check
        if not auth.has_permission(db_session, current_user, "perform_search"):
            thoughts.append("Permission denied: User does not have permission to perform searches.")
            raise HTTPException(status_code=403, detail="Permission denied: You do not have permission to perform searches.")

        thoughts.append(f"Search Agent received task: '{task}' with query: '{query}'")
        thoughts.append("Initiating search for external information and processing with DeepSeek...")

        # In a real implementation, this would involve calling an actual search API
        # (e.g., Google Search API, custom internal search).
        # For simulation, we'll use a placeholder.
        simulated_raw_search_results = [
            {"title": f"Simulated Search Result 1 for '{query}'", "url": "http://example.com/sim1", "snippet": "This is a snippet from a simulated search result."},
            {"title": f"Simulated Search Result 2 for '{query}'", "url": "http://example.com/sim2", "snippet": "Another snippet with relevant information."}
        ]
        if "no results" in query.lower():
            simulated_raw_search_results = []

        prompt = f"""
        You are a Search Result Processing AI (DeepSeek). Your task is to analyze raw search results and synthesize them into a concise and relevant summary or answer based on the user's query.

        User Query: {query}
        Raw Search Results: {json.dumps(simulated_raw_search_results, indent=2, ensure_ascii=False)}

        Provide your synthesized information in a JSON string with the following structure:
        {{
            "search_results": [ // List of processed relevant search results
                {{"title": "...", "url": "...", "snippet": "..."}},
                ...
            ],
            "message": "...", // Optional: A general message if no relevant info found
            "thoughts": ["...", "..."] // Your internal thoughts/reasoning.
        }}
        """

        try:
            deepseek_search_response_str = await llm_ollama_deepseek_ainvoke(prompt)
            thoughts.append(f"DeepSeek search processing raw response: {deepseek_search_response_str}")

            try:
                deepseek_parsed_response = json.loads(deepseek_search_response_str)
                output.update(deepseek_parsed_response)
                thoughts.extend(deepseek_parsed_response.get("thoughts", []))
                if "thoughts" in output:
                    del output["thoughts"]
            except json.JSONDecodeError:
                thoughts.append("DeepSeek search processing response was not valid JSON. Treating as plain text response.")
                output["search_results"] = []
                output["message"] = deepseek_search_response_str
                
        except Exception as e:
            output["error"] = f"Error calling DeepSeek LLM for search processing: {e}"
            thoughts.append(f"Error during DeepSeek search LLM call: {e}")
            output["message"] = f"An error occurred during search processing: {e}"

        thoughts.append("Search complete. Preparing output.")

        return {"output": output, "thoughts": thoughts}