from typing import Dict, Any, Tuple
from backend.proxy import permission_proxy

class BaseAgent:
    """Base class for governed logical AI agents."""
    agent_id: str
    role_name: str

    def execute_intent(
        self,
        user: str,
        tool: str,
        operation: str,
        customer_id: int,
        field: str = None,
        value: str = None,
        session_customer_id: int = 101
    ) -> Tuple[bool, str, Any, int]:
        """Dispatch intent execution through Permission Proxy Policy Decision Point."""
        return permission_proxy.evaluate_and_execute(
            user=user,
            agent=self.agent_id,
            tool=tool,
            operation=operation,
            customer_id=customer_id,
            field=field,
            value=value,
            session_customer_id=session_customer_id
        )


class SupportAgent(BaseAgent):
    """
    Support Agent.
    Permissions: Read Customer, Read Profile.
    Cannot: Update, Delete.
    """
    agent_id = "support_agent"
    role_name = "Support Agent"


class SalesAgent(BaseAgent):
    """
    Sales Agent.
    Permissions: Read, Update.
    Cannot: Delete.
    """
    agent_id = "sales_agent"
    role_name = "Sales Agent"


class AdminAgent(BaseAgent):
    """
    Admin Agent.
    Permissions: Read, Update, Delete.
    """
    agent_id = "admin_agent"
    role_name = "Admin Agent"


# Instantiated Logical Agents Registry
SUPPORT_AGENT = SupportAgent()
SALES_AGENT = SalesAgent()
ADMIN_AGENT = AdminAgent()

AGENTS_MAP = {
    "support_agent": SUPPORT_AGENT,
    "sales_agent": SALES_AGENT,
    "admin_agent": ADMIN_AGENT
}
