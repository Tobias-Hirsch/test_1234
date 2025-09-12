import json
from typing import Any, Dict, Optional
from .base_agent import BaseAgent
from app.llm.llm import llm_ollama_qwen_ainvoke # Import the Qwen LLM call

class FormattingOutputAgent(BaseAgent):
    """
    The Formatting/Output Agent (Qwen2.5) receives validated output and internal thoughts.
    It uses its function calling capabilities to format the output into a structured format
    and conditionally includes or filters the "thinking" process based on instructions.
    """

    def __init__(self):
        super().__init__(name="Formatting/Output Agent",
                         description="Formats output and manages display of thoughts using Qwen2.5.")

    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats the raw output and orchestrator thoughts into a final user-facing response
        using Qwen2.5 for structured output.

        Args:
            task (str): The specific formatting task (e.g., "format_response").
            context (Dict[str, Any]): A dictionary containing:
                                       - 'raw_output': The main output from other agents.
                                       - 'orchestrator_thoughts': Thoughts from the Orchestrator.
                                       - 'display_thoughts': Boolean indicating whether to display thoughts.
                                       - Other agents' thoughts (e.g., 'reasoning_thoughts', 'validation_thoughts').

        Returns:
            Dict[str, Any]: The final formatted response for the user.
        """
        final_response = {}
        thoughts = [] # Initialize thoughts list
        raw_output = context.get("raw_output", {})
        orchestrator_thoughts = context.get("orchestrator_thoughts", [])
        display_thoughts = context.get("display_thoughts", False)

        # Collect thoughts from all agents if available and display_thoughts is True
        all_thoughts = []
        if display_thoughts:
            all_thoughts.extend(orchestrator_thoughts)
            # Assuming other agents' thoughts are passed in context under specific keys
            for key, value in context.items():
                if key.endswith("_thoughts") and isinstance(value, list) and key != "orchestrator_thoughts":
                    all_thoughts.extend(value)

        # Construct the prompt for Qwen2.5 to perform formatting
        # This prompt will guide Qwen2.5 to use its "function calling" capability
        # to structure the output.
        prompt_content = {
            "raw_output": raw_output,
            "all_thoughts": all_thoughts if display_thoughts else [],
            "display_thoughts_requested": display_thoughts
        }
        
        prompt = f"""
        You are a sophisticated formatting and output generation AI (Qwen2.5). Your primary role is to take raw data and internal thoughts from other AI agents and format them into a clear, structured, and user-friendly response. You should leverage your function calling capabilities to achieve this.

        Here is the raw data and thoughts you need to process:
        {json.dumps(prompt_content, indent=2, ensure_ascii=False)}

        Based on the 'raw_output' content, determine the most appropriate formatting function to call.
        
        Available formatting functions (conceptual, you will generate the structured output directly):
        - `format_plan_markdown(plan_details: str, mermaid_diagram_code: Optional[str] = None)`: For detailed plans, optionally with Mermaid diagrams.
        - `format_code_response(code_snippet: str, language: str = "python")`: For code snippets.
        - `format_debugging_response(diagnosis: str, steps_to_fix: List[str])`: For debugging outputs.
        - `format_rag_results(rag_results: List[Dict[str, Any]])`: For RAG search results.
        - `format_search_results(search_results: List[Dict[str, Any]])`: For general search results.
        - `format_extracted_text(text: str)`: For extracted text from files.
        - `format_image_description(description: str)`: For image descriptions.
        - `format_general_response(response: str)`: For general text responses.
        - `format_error_response(error_message: str, details: Optional[str] = None)`: For error messages.

        Your final output should be a JSON string with the following structure, representing the "function call" you would conceptually make, or the direct structured output:
        {{
            "final_user_response": "...", // The main formatted content for the user
            "agent_thoughts": ["...", "..."] // Only include if 'display_thoughts_requested' is true and there are thoughts
        }}

        If the raw_output contains an "error" key, prioritize formatting it as an error response.
        """

        try:
            # Call the Qwen2.5 LLM
            qwen_response_str = await llm_ollama_qwen_ainvoke(prompt)
            thoughts.append(f"Qwen2.5 raw response: {qwen_response_str}")

            # Attempt to parse the response as JSON
            try:
                qwen_parsed_response = json.loads(qwen_response_str)
                final_response["output"] = qwen_parsed_response.get("final_user_response", "No formatted response from Qwen2.5.")
                if display_thoughts and qwen_parsed_response.get("agent_thoughts"):
                    final_response["thoughts"] = qwen_parsed_response.get("agent_thoughts")
            except json.JSONDecodeError:
                thoughts.append("Qwen2.5 response was not valid JSON. Treating as plain text response.")
                final_response["output"] = qwen_response_str
                if display_thoughts and all_thoughts:
                    final_response["thoughts"] = all_thoughts
                
        except Exception as e:
            final_response["output"] = f"An error occurred during formatting: {e}"
            if display_thoughts and all_thoughts:
                final_response["thoughts"] = all_thoughts
            thoughts.append(f"Error during Qwen2.5 LLM call: {e}")

        return final_response

    # These helper methods are now conceptual representations of what Qwen2.5 would do
    # via its function calling, rather than direct Python calls within this agent.
    # They are kept here for clarity on the desired output structure.

    def _format_plan_markdown(self, plan_details: str, mermaid_diagram_code: Optional[str] = None) -> str:
        """Conceptual: Formats a plan into markdown, optionally including a Mermaid diagram."""
        formatted_plan = f"### **Plan Details**\n{plan_details}\n"
        if mermaid_diagram_code:
            formatted_plan += f"\n### **Mermaid Diagram**\n```mermaid\n{mermaid_diagram_code}\n```\n"
        return formatted_plan

    def _format_rag_response(self, rag_results: list) -> str:
        """Conceptual: Formats RAG results into a readable string."""
        if not rag_results:
            return "No relevant RAG information found."
        
        formatted_str = "### **Relevant RAG Information**\n"
        for i, item in enumerate(rag_results):
            formatted_str += f"**Document {i+1} (ID: {item.get('document_id', 'N/A')}):**\n"
            formatted_str += f"{item.get('content', 'No content available.')}\n\n"
        return formatted_str

    def _format_search_results(self, search_results: list) -> str:
        """Conceptual: Formats search results into a readable string."""
        if not search_results:
            return "No search results found."
        
        formatted_str = "### **Search Results**\n"
        for i, item in enumerate(search_results):
            formatted_str += f"**{i+1}. {item.get('title', 'N/A')}**\n"
            formatted_str += f"URL: {item.get('url', 'N/A')}\n"
            formatted_str += f"Snippet: {item.get('snippet', 'No snippet available.')}\n\n"
        return formatted_str