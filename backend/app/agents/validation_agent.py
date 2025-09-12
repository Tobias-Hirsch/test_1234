import os
import json
import re # Import the regex module
from typing import Any, Dict, Optional
from .base_agent import BaseAgent
from app.llm.llm import llm_ollama_deepseek_ainvoke # Assuming DeepSeek for validation logic
from ..core.config import settings # Global import

class ValidationAgent(BaseAgent):
    """
    The Validation Agent evaluates temporary outputs based on user prompts,
    context, and predefined criteria. It includes a retry mechanism.
    """

    def __init__(self):
        super().__init__(name="Validation Agent",
                         description="Evaluates and validates agent outputs with retry logic.")
        self.max_retries = settings.MAX_VALIDATION_RETRIES # Default to 3 retries

    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an output and provides feedback for regeneration if needed.

        Args:
            task (str): The specific validation task (e.g., "validate_output", "validate_code").
            context (Dict[str, Any]): A dictionary containing:
                                       - 'output_to_validate': The output from another agent.
                                       - 'user_prompt': The original user prompt.
                                       - 'context': The overall conversation context.
                                       - 'retry_count' (Optional): Current retry attempt.
                                       - 'agent_name': The name of the agent whose output is being validated.

        Returns:
            Dict[str, Any]: A dictionary with validation status and potentially feedback.
                            Expected keys:
                            - 'status': "success" or "failure".
                            - 'validated_output' (Optional): The validated output if successful.
                            - 'feedback' (Optional): Feedback for regeneration if failed.
                            - 'thoughts' (Optional): Internal thoughts or reasoning.
        """
        thoughts = []
        output_to_validate = context.get("output_to_validate")
        user_prompt = context.get("user_prompt")
        current_context = context.get("context")
        retry_count = context.get("retry_count", 0)
        agent_name = context.get("agent_name", "Unknown Agent")

        # Create a serializable version of the context for the LLM prompt
        serializable_context = {k: v for k, v in current_context.items() if k not in ["db_session", "current_user", "files"]}

        thoughts.append(f"Validation Agent received output from '{agent_name}' for task: '{task}' (Retry: {retry_count})")
        thoughts.append("Evaluating output against user prompt and context using DeepSeek...")

        # Construct prompt for DeepSeek to perform validation
        validation_prompt = f"""
        You are a validation AI. Your task is to evaluate the provided 'output_to_validate' from '{agent_name}' against the 'user_prompt' and 'context'.
        Determine if the output is satisfactory, complete, and directly addresses the user's request.
        If the output indicates that no relevant information was found (e.g., empty RAG results),
        consider this valid if the process was completed without errors and the message is informative.
        
        User Prompt: {user_prompt}
        Overall Context: {json.dumps(serializable_context, indent=2, ensure_ascii=False)}
        Output to Validate from {agent_name}: {json.dumps(output_to_validate, indent=2, ensure_ascii=False)}

        Provide your evaluation in a JSON string with the following structure:
        {{
            "is_valid": true/false,
            "feedback": "...", // Detailed feedback if not valid, explaining what needs to be improved.
            "thoughts": ["...", "..."] // Your internal thoughts/reasoning during validation.
        }}
        """

        try:
            deepseek_validation_response_str = await llm_ollama_deepseek_ainvoke(validation_prompt)
            thoughts.append(f"DeepSeek Validation raw response: {deepseek_validation_response_str}")

            try:
                # Attempt to extract JSON from the response, in case it's wrapped in markdown or has extra text
                json_match = re.search(r"```json\s*(.*?)\s*```", deepseek_validation_response_str, re.DOTALL)
                if json_match:
                    json_string = json_match.group(1)
                    thoughts.append("Extracted JSON block from DeepSeek response.")
                else:
                    json_string = deepseek_validation_response_str.strip() # Try to strip whitespace if no markdown block
                    thoughts.append("No JSON block found, attempting to parse raw response after stripping whitespace.")

                validation_result_from_llm = json.loads(json_string)
                is_valid = validation_result_from_llm.get("is_valid", False)
                feedback = validation_result_from_llm.get("feedback", "No specific feedback provided.")
                thoughts.extend(validation_result_from_llm.get("thoughts", []))
            except json.JSONDecodeError as e: # Catch the specific error
                thoughts.append(f"DeepSeek validation response was not valid JSON. Error: {e}. Raw response: {deepseek_validation_response_str}. Assuming invalid.")
                is_valid = False
                feedback = "Validation model returned malformed response. Cannot validate."
            except Exception as e: # Catch any other unexpected errors during parsing
                thoughts.append(f"Unexpected error during DeepSeek validation response parsing: {e}. Raw response: {deepseek_validation_response_str}. Assuming invalid.")
                is_valid = False
                feedback = f"An unexpected error occurred during validation response parsing: {e}. Cannot validate."

        except Exception as e:
            thoughts.append(f"Error calling DeepSeek for validation: {e}")
            is_valid = False
            feedback = f"An error occurred during validation: {e}"

        if is_valid:
            thoughts.append("Output deemed valid.")
            return {
                "status": "success",
                "validated_output": output_to_validate,
                "thoughts": thoughts
            }
        else:
            thoughts.append("Output deemed invalid. Providing feedback for regeneration.")
            
            if retry_count >= self.max_retries:
                thoughts.append(f"Max retries ({self.max_retries}) reached. Validation failed permanently.")
                return {
                    "status": "failure",
                    "error": "Validation failed after multiple retries.",
                    "feedback": feedback,
                    "thoughts": thoughts
                }
            else:
                thoughts.append(f"Retrying... Current retry count: {retry_count + 1}")
                return {
                    "status": "failure",
                    "feedback": feedback,
                    "retry_needed": True,
                    "new_retry_count": retry_count + 1,
                    "thoughts": thoughts
                }