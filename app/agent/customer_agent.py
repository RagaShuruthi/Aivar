import time
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.llm.gemini import gemini_llm
from app.models.permission import ToolCallPayload, SessionContext, PermissionDecision
from app.models.crm import CustomerUpdate
from app.core.engine import permission_engine
from app.services.crm_service import CRMService
from app.services.audit_service import AuditService
from app.core.security import SecurityAlertService
from app.tools.registry import ToolRegistry

class AICustomerAgent:
    """
    Unified Role-Based AI Customer Assistant Agent Orchestrator.
    
    SECURITY INVARIANTS:
    1. Never trust LLM output blindly. Sanitize and validate every extracted field.
    2. NEVER invoke CRM directly. ALWAYS route through PermissionEngine Policy Decision Point.
    3. Calculate execution latency for governance observability and explainable AI traces.
    """

    @classmethod
    def process_query(
        cls,
        db: Session,
        prompt: str,
        agent_id: str = "support_agent",
        session_customer_id: int = 101
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Step 1: Send prompt to Gemini 2.5 Flash LLM (Tool Calling Model)
        json_intent = gemini_llm.extract_tool_intent(
            prompt=prompt,
            agent_id=agent_id,
            default_customer_id=session_customer_id
        )

        # Step 2: Strict Field Validation & Tool Registry Check
        tool_name = str(json_intent.get("tool", "crm")).lower()
        operation = str(json_intent.get("operation", "read")).lower()
        target_customer_id = int(json_intent.get("customer_id", session_customer_id))
        fields = json_intent.get("fields", {})

        # Validate against registered tools
        if not ToolRegistry.get(tool_name):
            tool_name = "crm"
            
        if operation not in ["read", "update", "delete"]:
            operation = "read"

        # Step 3: Construct ToolCallPayload for Proxy Mediation
        payload = ToolCallPayload(
            agent_id=agent_id,
            tool_name=tool_name,
            operation=operation,
            target_customer_id=target_customer_id,
            session_context=SessionContext(customer_id=session_customer_id),
            payload_data=fields if fields else None
        )

        # Step 4: PERMISSION ENGINE ENFORCEMENT (Proxy Layer PDP)
        decision: PermissionDecision = permission_engine.evaluate(payload)

        # Step 5: AUDIT LOGGING - Persist evaluation record to SQLite
        audit_entry = AuditService.log_decision(db, decision)

        # Step 6: Handle BLOCKED Denial
        if not decision.allowed:
            SecurityAlertService.check_and_trigger_alert(db, agent_id)
            exec_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "allowed": False,
                "reason": decision.reason,
                "agent_id": agent_id,
                "operation": operation,
                "tool": tool_name,
                "customer_id": target_customer_id,
                "session_customer_id": session_customer_id,
                "audit_log_id": audit_entry.id,
                "execution_time_ms": exec_time,
                "json_intent": json_intent,
                "permission_decision": decision.model_dump(),
                "data": None
            }

        # Step 7: Handle ALLOWED Execution via Proxy-Governed Tool Registry
        crm_data = None

        if operation == "read":
            customer = CRMService.get_customer_by_id(db, target_customer_id)
            if customer:
                crm_data = {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "company": customer.company,
                    "phone": customer.phone,
                    "status": "Active VIP",
                    "balance": "$4,250.00",
                    "recent_activity": "Logged in 5 mins ago"
                }

        elif operation == "update":
            update_data = fields if fields else {"name": "Alice Vance"}
            update_schema = CustomerUpdate(**update_data)
            updated_cust = CRMService.update_customer(db, target_customer_id, update_schema)
            if updated_cust:
                crm_data = {
                    "id": updated_cust.id,
                    "name": updated_cust.name,
                    "email": updated_cust.email,
                    "company": updated_cust.company,
                    "phone": updated_cust.phone,
                    "status": "Updated",
                    "balance": "$4,250.00",
                    "recent_activity": "Profile details updated via AI Assistant"
                }

        elif operation == "delete":
            deleted = CRMService.delete_customer(db, target_customer_id)
            if deleted:
                crm_data = {
                    "deleted_customer_id": target_customer_id,
                    "status": "Deleted",
                    "message": f"Customer account #{target_customer_id} permanently removed."
                }

        exec_time = round((time.time() - start_time) * 1000, 2)

        return {
            "allowed": True,
            "reason": decision.reason,
            "agent_id": agent_id,
            "operation": operation,
            "tool": tool_name,
            "customer_id": target_customer_id,
            "session_customer_id": session_customer_id,
            "audit_log_id": audit_entry.id,
            "execution_time_ms": exec_time,
            "json_intent": json_intent,
            "permission_decision": decision.model_dump(),
            "data": crm_data
        }
