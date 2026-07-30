from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PermissionManifest(BaseModel):
    """Declarative JSON policy schema assigned to an AI agent role."""
    agent_id: str = Field(..., example="support_agent")
    tool_name: str = Field(..., example="crm")
    allowed_operations: List[Literal["read", "update", "delete"]] = Field(..., example=["read"])
    data_scope: Literal["session_customer", "global", "none"] = Field(..., example="session_customer")

class SessionContext(BaseModel):
    """Runtime context passed alongside an agent request (e.g. current logged-in customer)."""
    customer_id: Optional[int] = Field(None, example=101)

class ToolCallPayload(BaseModel):
    """Payload sent by an AI Agent when invoking a tool via the proxy."""
    agent_id: str = Field(..., example="support_agent")
    tool_name: str = Field(..., example="crm")
    operation: Literal["read", "update", "delete"] = Field(..., example="read")
    target_customer_id: int = Field(..., example=101)
    session_context: SessionContext
    payload_data: Optional[dict] = Field(None, description="Optional payload body for update operations")

class PermissionDecision(BaseModel):
    """Result returned by the Permission Engine evaluation."""
    allowed: bool
    reason: str
    agent_id: str
    tool_name: str
    operation: str
    target_customer_id: int
