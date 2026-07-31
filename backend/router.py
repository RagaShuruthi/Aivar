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
        operation = str(structured_intent.get("operation", "read")).lower()
        if operation == "chat":
            return True, "Conversational Query - No CRM Tool Execution Required.", None, 0, "general_assistant"

        if operation == "audit":
            from backend.logger import audit_logger
            logs = audit_logger.get_logs(limit=5)
            if not logs:
                summary_text = "No recent audit activity recorded yet."
            else:
                formatted_lines = []
                for l in logs:
                    u_name = l.get('user', 'User')
                    op = l.get('operation', 'action').lower()
                    cid = l.get('customer_id', '')
                    is_allowed = l.get('allowed', False)
                    status_str = "Allowed" if is_allowed else "Blocked (Role Restriction)"

                    if is_allowed:
                        if op == "update":
                            detail = f"Updated details for Customer #{cid}"
                        elif op == "delete":
                            detail = f"Deleted Customer #{cid}"
                        elif op == "create":
                            detail = f"Created new record for Customer #{cid}"
                        else:
                            detail = f"Retrieved profile for Customer #{cid}"
                    else:
                        detail = f"Attempted {op} operation on Customer #{cid}"

                    formatted_lines.append(f"• **{u_name}**: {detail} — *{status_str}*")

                summary_text = "Here is the recent activity audit history:\n\n" + "\n".join(formatted_lines)
            
            return True, summary_text, {"audit_history": logs, "summary": summary_text}, 0, "audit_service"


        if operation == "permission_info":
            resolved_role = active_role_override or "support_agent"
            target_agent = AGENTS_MAP.get(resolved_role.lower(), SUPPORT_AGENT)
            manifest = target_agent.permission_proxy.manifest.get(resolved_role, {})
            allowed_ops = manifest.get("allowed_operations", [])
            scope = manifest.get("scope", "session_customer_only")
            
            perm_text = (
                f"Your Session Permission Metadata:\n"
                f"• Active Role: {resolved_role.upper()}\n"
                f"• Authorized Operations: {', '.join(allowed_ops)}\n"
                f"• Access Scope: {scope}\n"
                f"• Session Customer ID: #{session_customer_id}"
            )
            return True, perm_text, {"permissions": manifest}, 0, "permission_engine"


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
