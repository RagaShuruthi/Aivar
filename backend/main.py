from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from backend.gemini import gemini_service
from backend.router import agent_router_service
from backend.crm import crm_db
from backend.logger import audit_logger
from backend.proxy import permission_proxy

app = FastAPI(
    title="Agentic AI CRM Assistant with Permission Proxy",
    version="2.0.0",
    description="Enterprise AI CRM Platform enforcing Zero-Trust Permission Proxy Policy Enforcement."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user: str = Field("Alice Smith", example="Alice Smith")
    agent_role: str = Field("support_agent", example="support_agent")
    prompt: str = Field(..., example="Show customer 101")
    session_customer_id: int = Field(101, example=101)

class ChatResponse(BaseModel):
    allowed: bool
    reason: str
    response_text: str
    intent: Dict[str, Any]
    agent_executed: str
    audit_log_id: int
    data: Optional[Any] = None

@app.get("/health", tags=["Health Probe"])
def health_check():
    return {"status": "healthy", "service": "Agentic AI CRM Permission Proxy"}

@app.get("/api/v1/customers", tags=["CRM Data"])
def get_customers():
    """Fetch list of all 20 CRM customer profiles."""
    return {"customers": crm_db.get_all_customers()}

@app.get("/api/v1/audit-logs", tags=["Audit Observability"])
def get_audit_logs(limit: int = 100):
    """Fetch immutable audit log stream."""
    return {"logs": audit_logger.get_logs(limit=limit)}

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["AI CRM Pipeline"])
def process_chat_pipeline(payload: ChatRequest):
    """
    Main Agentic Execution Pipeline:
    1. Gemini Intent Detection (Prompt -> Structured JSON)
    2. Router Dispatch (Selects target AI Agent)
    3. Permission Proxy Enforcement (Validates manifest.json & Data Scope)
    4. Mock CRM Execution (Only if Allowed)
    5. Audit Logging (Immutable SQLite Log)
    6. Gemini Response Generator (Natural Language Response)
    """
    try:
        # Step 1: Gemini Intent Detection
        structured_intent = gemini_service.detect_intent(
            prompt=payload.prompt,
            default_customer_id=payload.session_customer_id,
            default_agent=payload.agent_role
        )

        # Step 2 & 3 & 4 & 5: Router -> Agent Dispatcher -> Permission Proxy -> CRM -> Audit Log
        allowed, reason, crm_data, audit_id, executed_agent = agent_router_service.dispatch(
            user=payload.user,
            structured_intent=structured_intent,
            session_customer_id=payload.session_customer_id,
            active_role_override=payload.agent_role
        )

        # Step 6: Gemini Natural Language Response Generator
        nl_response = gemini_service.generate_nl_response(
            prompt=payload.prompt,
            allowed=allowed,
            reason=reason,
            crm_data=crm_data,
            is_chat_only=(structured_intent.get("operation") == "chat"),
            operation=structured_intent.get("operation", "read"),
            target_customer_id=structured_intent.get("customer_id")
        )



        return ChatResponse(
            allowed=allowed,
            reason=reason,
            response_text=nl_response,
            intent=structured_intent,
            agent_executed=executed_agent,
            audit_log_id=audit_id,
            data=crm_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}"
        )
