import json
from typing import Any, Dict, Optional
from .base_agent import BaseAgent
from app.llm.llm import llm_ollama_deepseek_ainvoke # Assuming DeepSeek for code generation

class CodeGenerationAgent(BaseAgent):
    """
    The Code Generation Agent is responsible for generating code snippets or
    full code solutions based on the task and context.
    """

    def __init__(self):
        super().__init__(name="Code Generation Agent",
                         description="Generates code snippets or full code solutions.")

    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates code based on the provided task and context using DeepSeek.

        Args:
            task (str): The specific code generation task (e.g., "generate_python_function").
            context (Dict[str, Any]): A dictionary containing:
                                       - 'requirements': Detailed requirements for the code.
                                       - 'existing_code' (Optional): Existing code to modify.
                                       - 'user_prompt': The original user prompt.
                                       - 'feedback' (Optional): Feedback from Validation Agent for regeneration.
                                       - Other relevant context.

        Returns:
            Dict[str, Any]: A dictionary containing the generated code and thoughts.
        """
        thoughts = []
        output = {}
        requirements = context.get("requirements", task)
        existing_code = context.get("existing_code", "")
        user_prompt = context.get("user_prompt", "")
        feedback = context.get("feedback", "")

        thoughts.append(f"Code Generation Agent received task: '{task}' with requirements: '{requirements}'")
        thoughts.append("Generating code based on requirements using DeepSeek...")

        existing_code_part = ""
        if existing_code:
            existing_code_part = f"Existing Code to Consider/Modify:\n```\n{existing_code}\n```\n"

        feedback_part = ""
        if feedback:
            feedback_part = f"Feedback for Regeneration: {feedback}\n"

        prompt = f"""
        You are a Code Generation AI (DeepSeek). Your task is to generate code based on the provided requirements and context.
        
        User Prompt: {user_prompt}
        Code Generation Task: {task}
        Requirements: {requirements}
        
        {existing_code_part}{feedback_part}
        Provide the generated code in a JSON string with the following structure:
        {{
            "generated_code": "...", // The generated code string
            "language": "python", // The language of the generated code (e.g., "python", "javascript")
            "thoughts": ["...", "..."] // Your internal thoughts/reasoning.
        }}
        """

        try:
            deepseek_code_response_str = await llm_ollama_deepseek_ainvoke(prompt)
            thoughts.append(f"DeepSeek code generation raw response: {deepseek_code_response_str}")

            try:
                deepseek_parsed_response = json.loads(deepseek_code_response_str)
                output.update(deepseek_parsed_response)
                thoughts.extend(deepseek_parsed_response.get("thoughts", []))
                if "thoughts" in output:
                    del output["thoughts"]
            except json.JSONDecodeError:
                thoughts.append("DeepSeek code generation response was not valid JSON. Treating generated code as plain text.")
                output["generated_code"] = deepseek_code_response_str
                output["language"] = "python" # Default if parsing fails
                
        except Exception as e:
            output["error"] = f"Error calling DeepSeek LLM for code generation: {e}"
            thoughts.append(f"Error during DeepSeek code generation LLM call: {e}")
            output["generated_code"] = f"# Error generating code: {e}"
            output["language"] = "python"

        thoughts.append("Code generation complete. Preparing output.")

        return {"output": output, "thoughts": thoughts}