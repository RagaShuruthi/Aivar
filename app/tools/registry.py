from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    Abstract Base Class for Enterprise Tools registered in the AI Governance Platform.
    Enables zero-friction registration of future tools (Email, Calendar, Payments, Inventory, Ticketing).
    """
    name: str
    description: str

    @abstractmethod
    def execute(self, operation: str, target_id: int, payload_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool operation."""
        pass


class CRMTool(BaseTool):
    """CRM Tool implementation interfacing with customer data."""
    name = "crm"
    description = "Enterprise CRM database for customer accounts, balances, and contact details."

    def execute(self, operation: str, target_id: int, payload_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": "success",
            "tool": self.name,
            "operation": operation,
            "target_id": target_id
        }


class EmailTool(BaseTool):
    """Future Email Tool for sending customer emails."""
    name = "email"
    description = "Enterprise Email Dispatcher Service."

    def execute(self, operation: str, target_id: int, payload_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "success", "tool": self.name, "operation": operation}


class ToolRegistry:
    """Centralized Registry for Enterprise AI Tools."""
    _registry: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """Register a tool instance."""
        cls._registry[tool.name.lower()] = tool

    @classmethod
    def get(cls, tool_name: str) -> Optional[BaseTool]:
        """Retrieve a registered tool by name."""
        return cls._registry.get(tool_name.lower())

    @classmethod
    def list_tools(cls) -> List[str]:
        """List names of all registered tools."""
        return list(cls._registry.keys())


# Register core default tools on module load
ToolRegistry.register(CRMTool())
ToolRegistry.register(EmailTool())
