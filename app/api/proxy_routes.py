from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.permission import ToolCallPayload, PermissionDecision
from app.models.crm import CustomerUpdate
from app.core.engine import permission_engine
from app.services.crm_service import CRMService
from app.services.audit_service import AuditService
from app.core.security import SecurityAlertService

router = APIRouter(prefix="/proxy", tags=["Tool Permission Proxy"])

@router.post("/invoke-tool", status_code=status.HTTP_200_OK)
def invoke_tool(payload: ToolCallPayload, db: Session = Depends(get_db)):
    """
    Main Gateway Endpoint for AI Agents.
    Intercepts tool calls, enforces permission manifests, records audit logs,
    triggers security alerts on policy breaches, and forwards permitted calls to CRM API.
    """
    # 1. Evaluate incoming request against Permission Engine
    decision: PermissionDecision = permission_engine.evaluate(payload)

    # 2. AUDIT LOGGING: Record every decision (Allowed or Blocked) in SQLite
    AuditService.log_decision(db, decision)

    # 3. SECURITY ALERTING: If blocked, check if agent exceeded >3 blocked attempts
    if not decision.allowed:
        SecurityAlertService.check_and_trigger_alert(db, decision.agent_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Permission Denied by Tool Permission Enforcer",
                "reason": decision.reason,
                "agent_id": decision.agent_id,
                "tool_name": decision.tool_name,
                "operation": decision.operation,
                "target_customer_id": decision.target_customer_id
            }
        )

    # 3. If ALLOWED, forward request to downstream CRM Service
    result = None

    if payload.operation == "read":
        customer = CRMService.get_customer_by_id(db, payload.target_customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {payload.target_customer_id} not found."
            )
        result = {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "company": customer.company,
            "phone": customer.phone
        }

    elif payload.operation == "update":
        if not payload.payload_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payload_data is required for update operation."
            )
        update_schema = CustomerUpdate(**payload.payload_data)
        updated_customer = CRMService.update_customer(db, payload.target_customer_id, update_schema)
        if not updated_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {payload.target_customer_id} not found."
            )
        result = {
            "id": updated_customer.id,
            "name": updated_customer.name,
            "email": updated_customer.email,
            "company": updated_customer.company,
            "phone": updated_customer.phone
        }

    elif payload.operation == "delete":
        deleted = CRMService.delete_customer(db, payload.target_customer_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {payload.target_customer_id} not found."
            )
        result = {"message": f"Customer {payload.target_customer_id} deleted successfully."}

    # 4. Return successful response with execution result and permission decision metadata
    return {
        "status": "success",
        "permission_decision": {
            "allowed": True,
            "reason": decision.reason
        },
        "data": result
    }
