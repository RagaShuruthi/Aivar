from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    """Base Pydantic schema shared across Customer operations."""
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    """Schema used when creating a new Customer record."""
    pass

class CustomerUpdate(BaseModel):
    """Schema used for partial or full customer profile updates."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None

class CustomerResponse(CustomerBase):
    """Schema returned in API responses, including database IDs and timestamps."""
    id: int
    created_at: datetime
    updated_at: datetime

    # ConfigDict(from_attributes=True) allows Pydantic to convert SQLAlchemy ORM objects directly into JSON DTOs
    model_config = ConfigDict(from_attributes=True)
