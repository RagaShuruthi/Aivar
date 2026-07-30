from sqlalchemy.orm import Session
from typing import Dict, Any
from app.llm.gemini import gemini_llm
from app.models.permission import ToolCallPayload, SessionContext, PermissionDecision
from app.models.crm import CustomerUpdate
from app.core.engine import permission_engine
from app.services.crm_service import CRMService
from app.services.audit_service import AuditService
from app.core.security import SecurityAlertService

class AICustomerAgent:
    """
    AI Customer Assistant Agent Orchestrator.
    
    SECURITY ARCHITECTURE:
    1. Gemini LLM extracts tool call intent from natural language.
    2. Payload is sent to Tool Permission Enforcer (PermissionEngine).
    3. Permission Engine evaluates ABAC policies and logs audit trail.
    4. IF ALLOWED: Executes downstream CRM operation.
    5. IF BLOCKED: Stops execution, logs breach, triggers threat detection if >3 violations.
    """

    @classmethod
    def process_query(
        cls,
        db: Session,
        prompt: str,
        agent_id: str = "support_agent",
        session_customer_id: int = 101
    ) -> Dict[str, Any]:
        
        # Step 1: Extract tool call intent via Gemini LLM
        intent = gemini_llm.extract_tool_intent(prompt, default_customer_id=session_customer_id)

        # Step 2: Construct ToolCallPayload object
        payload = ToolCallPayload(
            agent_id=agent_id,
            tool_name=intent.get("tool_name", "crm"),
            operation=intent.get("operation", "read"),
            target_customer_id=intent.get("target_customer_id", session_customer_id),
            session_context=SessionContext(customer_id=session_customer_id),
            payload_data=intent.get("payload_data")
        )

        # Step 3: PERMISSION ENFORCEMENT - Evaluate payload against Permission Engine
        decision: PermissionDecision = permission_engine.evaluate(payload)

        # Step 4: AUDIT LOGGING - Record evaluation outcome in SQLite
        audit_entry = AuditService.log_decision(db, decision)

        # Step 5: Handle Denial (403 BLOCKED)
        if not decision.allowed:
            # Trigger threat detection check for >3 blocked requests
            SecurityAlertService.check_and_trigger_alert(db, agent_id)

            bot_response = (
                f"🚫 **Access Denied by Tool Permission Enforcer**\n\n"
                f"**Reason:** {decision.reason}\n\n"
                f"*Security Policy Constraint: Agent `{agent_id}` is not authorized to execute `{payload.operation}` on target Customer ID `{payload.target_customer_id}`.*"
            )

            return {
                "response": bot_response,
                "allowed": False,
                "reason": decision.reason,
                "audit_log_id": audit_entry.id,
                "tool_call_payload": payload.model_dump(),
                "permission_decision": decision.model_dump(),
                "data": None
            }

        # Step 6: Handle Authorized Execution (200 ALLOWED)
        crm_result = None

        if payload.operation == "read":
            customer = CRMService.get_customer_by_id(db, payload.target_customer_id)
            if customer:
                crm_result = {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "company": customer.company,
                    "phone": customer.phone
                }
                bot_response = (
                    f"✅ **Customer Profile Retrieved Successfully**\n\n"
                    f"- **Customer ID:** `{customer.id}`\n"
                    f"- **Name:** {customer.name}\n"
                    f"- **Email:** {customer.email}\n"
                    f"- **Company:** {customer.company}\n"
                    f"- **Phone:** {customer.phone}"
                )
            else:
                bot_response = f"⚠️ Customer with ID `{payload.target_customer_id}` was not found in the CRM database."

        elif payload.operation == "update":
            payload_dict = payload.payload_data or {"name": "Updated Profile"}
            update_schema = CustomerUpdate(**payload_dict)
            updated_cust = CRMService.update_customer(db, payload.target_customer_id, update_schema)
            if updated_cust:
                crm_result = {
                    "id": updated_cust.id,
                    "name": updated_cust.name,
                    "email": updated_cust.email,
                    "company": updated_cust.company,
                    "phone": updated_cust.phone
                }
                bot_response = f"✅ **Customer Profile Updated Successfully!** Name is now: **{updated_cust.name}**."
            else:
                bot_response = f"⚠️ Customer ID `{payload.target_customer_id}` not found for update."

        elif payload.operation == "delete":
            deleted = CRMService.delete_customer(db, payload.target_customer_id)
            if deleted:
                crm_result = {"deleted_id": payload.target_customer_id}
                bot_response = f"✅ **Customer ID `{payload.target_customer_id}` has been deleted from the CRM database.**"
            else:
                bot_response = f"⚠️ Customer ID `{payload.target_customer_id}` not found for deletion."

        return {
            "response": bot_response,
            "allowed": True,
            "reason": decision.reason,
            "audit_log_id": audit_entry.id,
            "tool_call_payload": payload.model_dump(),
            "permission_decision": decision.model_dump(),
            "data": crm_result
        }
