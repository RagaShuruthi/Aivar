from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.agent.customer_agent import AICustomerAgent

router = APIRouter(prefix="/agent", tags=["AI Customer Assistant Agent"])

class ChatRequest(BaseModel):
    """Payload for natural language chat queries to the AI Assistant."""
    prompt: str = Field(..., example="Show details for customer 101")
    agent_id: str = Field("support_agent", example="support_agent")
    session_customer_id: int = Field(101, example=101)

@router.post("/chat")
def chat_with_agent(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Conversational API Endpoint for AI Customer Assistant.
    Routes natural language queries through Gemini LLM -> Permission Engine Proxy -> CRM API.
    """
    try:
        result = AICustomerAgent.process_query(
            db=db,
            prompt=payload.prompt,
            agent_id=payload.agent_id,
            session_customer_id=payload.session_customer_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(e)}"
        )
