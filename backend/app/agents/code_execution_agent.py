import subprocess
from typing import Any, Dict, Optional
from .base_agent import BaseAgent
from app.services import auth
from fastapi import HTTPException

class CodeExecutionAgent(BaseAgent):
    """
    The Code Execution Agent executes generated code in a safe and isolated environment.
    It provides execution results, including stdout, stderr, and any errors.
    """

    def __init__(self):
        super().__init__(name="Code Execution Agent",
                         description="Executes code in a safe environment and returns results.")

    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes code and captures its output, with integrated permission checks.

        Args:
            task (str): The specific execution task (e.g., "execute_python_code").
            context (Dict[str, Any]): A dictionary containing:
                                       - 'code': The code string to execute.
                                       - 'language': The programming language (e.g., "python", "javascript").
                                       - 'timeout' (Optional): Maximum execution time in seconds.

        Returns:
            Dict[str, Any]: A dictionary containing execution results (stdout, stderr, error) and thoughts.
        """
        thoughts = []
        output = {}
        code = context.get("code")
        language = context.get("language", "python") # Default to python
        timeout = context.get("timeout", 10) # Default timeout of 10 seconds
        db_session = context.get("db_session")
        current_user = context.get("current_user")

        # Permission check
        if not auth.has_permission(db_session, current_user, "execute_code"):
            thoughts.append("Permission denied: User does not have permission to execute code.")
            raise HTTPException(status_code=403, detail="Permission denied: You do not have permission to execute code.")

        thoughts.append(f"Code Execution Agent received task: '{task}' for {language} code.")
        thoughts.append("Preparing to execute code in an isolated environment...")

        if not code:
            output["error"] = "No code provided for execution."
            thoughts.append("Error: No code to execute.")
            return {"output": output, "thoughts": thoughts}

        try:
            if language == "python":
                # For a real system, use a more secure sandboxing mechanism (e.g., Docker, isolated process)
                process = await self._run_command_async(["python", "-c", code], timeout)
            elif language == "javascript":
                # Assuming Node.js is available
                process = await self._run_command_async(["node", "-e", code], timeout)
            else:
                output["error"] = f"Unsupported language for execution: {language}."
                thoughts.append(f"Error: Unsupported language {language}.")
                return {"output": output, "thoughts": thoughts}

            stdout, stderr = process.communicate()
            output["stdout"] = stdout.decode().strip()
            output["stderr"] = stderr.decode().strip()
            output["return_code"] = process.returncode

            if process.returncode != 0:
                output["error"] = f"Code execution failed with exit code {process.returncode}."
                thoughts.append(f"Code execution failed. Stderr: {output['stderr']}")
            else:
                thoughts.append("Code executed successfully.")

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            output["stdout"] = stdout.decode().strip()
            output["stderr"] = stderr.decode().strip()
            output["error"] = f"Code execution timed out after {timeout} seconds."
            thoughts.append("Error: Code execution timed out.")
        except Exception as e:
            output["error"] = f"An unexpected error occurred during code execution: {e}"
            thoughts.append(f"Error during execution: {e}")

        thoughts.append("Code execution complete. Preparing output.")

        return {"output": output, "thoughts": thoughts}

    async def _run_command_async(self, command: list[str], timeout: int):
        """Helper to run a command asynchronously."""
        return await subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)