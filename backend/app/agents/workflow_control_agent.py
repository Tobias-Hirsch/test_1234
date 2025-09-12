from typing import Any, Dict, Optional, Callable
from .base_agent import BaseAgent

class WorkflowControlAgent(BaseAgent):
    """
    The Workflow Control Agent manages complex, multi-step workflows,
    orchestrating interactions between other agents in a predefined sequence
    or dynamically based on conditions.
    """

    def __init__(self):
        super().__init__(name="Workflow Control Agent",
                         description="Manages and orchestrates complex multi-step workflows.")
        self.registered_workflows: Dict[str, Callable] = {}

    def register_workflow(self, workflow_name: str, workflow_function: Callable):
        """Registers a callable function as a workflow."""
        self.registered_workflows[workflow_name] = workflow_function

    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a predefined workflow or dynamically orchestrates agents.

        Args:
            task (str): The specific workflow task (e.g., "execute_code_workflow").
            context (Dict[str, Any]): Contextual information for the workflow.

        Returns:
            Dict[str, Any]: The final result of the workflow execution and thoughts.
        """
        thoughts = []
        output = {}
        workflow_name = context.get("workflow_name", task)

        thoughts.append(f"Workflow Control Agent received task: '{task}' for workflow: '{workflow_name}'")
        thoughts.append("Initiating workflow execution...")

        if workflow_name not in self.registered_workflows:
            output["error"] = f"Workflow '{workflow_name}' not registered."
            thoughts.append(f"Error: Workflow '{workflow_name}' not found.")
            return {"output": output, "thoughts": thoughts}

        try:
            # Execute the registered workflow function
            workflow_result = await self.registered_workflows[workflow_name](context)
            output.update(workflow_result)
            thoughts.append(f"Workflow '{workflow_name}' completed successfully.")
        except Exception as e:
            output["error"] = f"Error executing workflow '{workflow_name}': {e}"
            thoughts.append(f"Error during workflow execution: {e}")

        thoughts.append("Workflow execution complete. Preparing output.")

        return {"output": output, "thoughts": thoughts}

    # Example of a complex workflow that could be registered
    async def _example_code_development_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        An example workflow for code development:
        1. Generate code.
        2. Validate code.
        3. Execute code.
        """
        thoughts = []
        workflow_output = {}

        # Assume agents are passed in context or accessible via a global registry
        reasoning_agent = context.get("reasoning_agent")
        validation_agent = context.get("validation_agent")
        code_gen_agent = context.get("code_generation_agent")
        code_exec_agent = context.get("code_execution_agent")

        if not all([reasoning_agent, validation_agent, code_gen_agent, code_exec_agent]):
            return {"error": "Required agents not provided in context for workflow."}

        # Step 1: Reasoning/Planning to get requirements
        reasoning_result = await reasoning_agent.process("plan_code_development", context)
        thoughts.extend(reasoning_result.get("thoughts", []))
        requirements = reasoning_result.get("output", {}).get("requirements", "Implement a simple function.")
        
        # Step 2: Code Generation
        code_gen_result = await code_gen_agent.process("generate_code", {"requirements": requirements})
        thoughts.extend(code_gen_result.get("thoughts", []))
        generated_code = code_gen_result.get("output", {}).get("generated_code")

        if not generated_code:
            return {"error": "Code generation failed."}

        # Step 3: Validate Generated Code (with retries)
        validated_code = None
        for i in range(validation_agent.max_retries + 1):
            validation_context = {
                "output_to_validate": {"output": {"generated_code": generated_code}},
                "user_prompt": context.get("user_prompt", ""),
                "context": context,
                "retry_count": i
            }
            validation_result = await validation_agent.process("validate_code", validation_context)
            thoughts.extend(validation_result.get("thoughts", []))

            if validation_result.get("status") == "success":
                validated_code = generated_code
                thoughts.append("Code validated successfully.")
                break
            elif validation_result.get("retry_needed"):
                thoughts.append(f"Code validation failed. Retrying code generation with feedback: {validation_result.get('feedback')}")
                # In a real scenario, pass feedback to code_gen_agent for regeneration
                code_gen_result = await code_gen_agent.process("regenerate_code", {"requirements": requirements, "feedback": validation_result.get('feedback')})
                generated_code = code_gen_result.get("output", {}).get("generated_code")
                if not generated_code:
                    return {"error": "Code regeneration failed after validation feedback."}
            else:
                return {"error": f"Code validation failed permanently: {validation_result.get('error')}"}

        if not validated_code:
            return {"error": "Failed to generate valid code after retries."}

        # Step 4: Code Execution
        execution_result = await code_exec_agent.process("execute_python_code", {"code": validated_code, "language": "python"})
        thoughts.extend(execution_result.get("thoughts", []))
        
        workflow_output["final_code"] = validated_code
        workflow_output["execution_output"] = execution_result.get("output")
        workflow_output["workflow_status"] = "completed"

        return {"output": workflow_output, "thoughts": thoughts}