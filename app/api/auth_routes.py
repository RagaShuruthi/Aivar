from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.db.session import get_db
from app.services.crm_service import CRMService

router = APIRouter(prefix="/auth", tags=["Enterprise Demo Login"])

class DemoLoginRequest(BaseModel):
    """Payload for simple Demo Login (Name and Role only)."""
    name: str = Field(..., example="Shuruthi")
    role: str = Field(..., example="CRM Administrator")

class DemoUserResponse(BaseModel):
    """Response payload storing session metadata upon successful login."""
    name: str
    role: str           # admin_agent, support_agent, restricted_agent
    role_title: str     # CRM Administrator, Support Agent, Read Only
    customer_id: int
    email: str
    department: str
    city: str
    phone: str

@router.post("/demo-login", response_model=DemoUserResponse)
def demo_login(payload: DemoLoginRequest, db: Session = Depends(get_db)):
    """
    Validates Demo Login:
    1. Validates that the entered name exists in the mock CRM database.
    2. Validates that the selected role matches the user's registered role.
    3. Returns session user metadata if valid, else raises 'Invalid Name or Role.'
    """
    CRMService.seed_initial_data(db)
    customer = CRMService.validate_demo_login(db, payload.name, payload.role)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Name or Role."
        )

    return DemoUserResponse(
        name=customer.name,
        role=customer.role,
        role_title=customer.role_title,
        customer_id=customer.id,
        email=customer.email,
        department=customer.department or "Enterprise",
        city=customer.city or "San Francisco",
        phone=customer.phone or "+1-555-0100"
    )

@router.get("/mock-users", response_model=List[DemoUserResponse])
def get_mock_crm_users(db: Session = Depends(get_db)):
    """Fetch all 20 mock CRM user accounts for reference."""
    customers = CRMService.seed_initial_data(db)
    return [
        DemoUserResponse(
            name=c.name,
            role=c.role or "support_agent",
            role_title=c.role_title or "Support Agent",
            customer_id=c.id,
            email=c.email,
            department=c.department or "Enterprise",
            city=c.city or "San Francisco",
            phone=c.phone or "+1-555-0100"
        ) for c in customers
    ]
