from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    Defines the common interface for agent operations.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a given task with the provided context.
        This method must be implemented by all concrete agents.

        Args:
            task (str): The specific task to be performed by the agent.
            context (Dict[str, Any]): A dictionary containing relevant context
                                       for the task, such as user prompt,
                                       intermediate results, etc.

        Returns:
            Dict[str, Any]: A dictionary containing the result of the agent's
                            processing, including any generated thoughts.
                            Expected keys:
                            - 'output': The main output of the agent.
                            - 'thoughts' (Optional): Internal thoughts or reasoning.
        """
        pass

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description