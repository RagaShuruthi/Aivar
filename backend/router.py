from typing import Dict, Any, Tuple
from backend.agents import AGENTS_MAP, SUPPORT_AGENT
from backend.crm import crm_db

class AgentRouter:
    """
    Backend Router module automatically selecting and dispatching requests
    to the correct AI Agent based on the logged-in user's role.
    """

    @staticmethod
    def dispatch(
        user: str,
        structured_intent: Dict[str, Any],
        session_customer_id: int = 101,
        active_role_override: str = None
    ) -> Tuple[bool, str, Any, int, str]:
        """
        Determines target agent automatically from user session role and dispatches tool execution.
        Returns: (allowed, reason, result_data, audit_id, executed_agent_id)
        """
        # Resolve user role automatically from Mock CRM Database if not explicitly overridden
        resolved_role = active_role_override
        if not resolved_role:
            cust_record = crm_db.read_customer(session_customer_id)
            if cust_record and cust_record.get("role"):
                resolved_role = cust_record.get("role")
            else:
                resolved_role = structured_intent.get("agent", "support_agent")

        target_agent = AGENTS_MAP.get(resolved_role.lower(), SUPPORT_AGENT)

        tool = str(structured_intent.get("tool", "crm")).lower()
        operation = str(structured_intent.get("operation", "read")).lower()
        customer_id = int(structured_intent.get("customer_id", session_customer_id))
        field = structured_intent.get("field")
        value = structured_intent.get("value")

        allowed, reason, data, audit_id = target_agent.execute_intent(
            user=user,
            tool=tool,
            operation=operation,
            customer_id=customer_id,
            field=field,
            value=value,
            session_customer_id=session_customer_id
        )

        return allowed, reason, data, audit_id, target_agent.agent_id

# Singleton Router Instance
agent_router_service = AgentRouter()
