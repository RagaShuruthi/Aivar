from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.crm import CustomerResponse, CustomerUpdate, CustomerCreate
from app.services.crm_service import CRMService

router = APIRouter(prefix="/crm", tags=["Mock CRM API"])

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """Fetch details of a single customer by ID."""
    customer = CRMService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found."
        )
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, update_data: CustomerUpdate, db: Session = Depends(get_db)):
    """Update details of a specific customer by ID."""
    updated_customer = CRMService.update_customer(db, customer_id, update_data)
    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found."
        )
    return updated_customer

@router.delete("/customers/{customer_id}", status_code=status.HTTP_200_OK)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer record by ID."""
    deleted = CRMService.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found."
        )
    return {"message": f"Customer {customer_id} deleted successfully."}

@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    """List all customers in the CRM database."""
    return CRMService.get_all_customers(db)

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_customers(db: Session = Depends(get_db)):
    """Populate database with sample customer records (ID 101, 102, 103)."""
    seeded = CRMService.seed_initial_data(db)
    return {
        "message": "Mock CRM database seeded successfully.",
        "count": len(seeded),
        "customers": [c.id for c in seeded]
    }
