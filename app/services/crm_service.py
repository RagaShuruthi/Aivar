from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.models import CustomerModel
from app.models.crm import CustomerCreate, CustomerUpdate

class CRMService:
    """Service layer handling database operations for the Mock CRM API."""

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[CustomerModel]:
        """Fetch a single customer by primary key ID."""
        return db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()

    @staticmethod
    def get_all_customers(db: Session, limit: int = 100) -> List[CustomerModel]:
        """Fetch a list of all customers."""
        return db.query(CustomerModel).limit(limit).all()

    @staticmethod
    def create_customer(db: Session, customer_in: CustomerCreate) -> CustomerModel:
        """Create and persist a new customer record."""
        db_customer = CustomerModel(
            name=customer_in.name,
            email=customer_in.email,
            company=customer_in.company,
            phone=customer_in.phone
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    @staticmethod
    def update_customer(db: Session, customer_id: int, update_in: CustomerUpdate) -> Optional[CustomerModel]:
        """Update existing customer details dynamically."""
        db_customer = CRMService.get_customer_by_id(db, customer_id)
        if not db_customer:
            return None

        update_data = update_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_customer, key, value)

        db.commit()
        db.refresh(db_customer)
        return db_customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        """Delete a customer record from SQLite."""
        db_customer = CRMService.get_customer_by_id(db, customer_id)
        if not db_customer:
            return False

        db.delete(db_customer)
        db.commit()
        return True

    @staticmethod
    def seed_initial_data(db: Session) -> List[CustomerModel]:
        """Seeds SQLite database with sample customer profiles for testing."""
        if db.query(CustomerModel).count() > 0:
            return db.query(CustomerModel).all()

        sample_customers = [
            CustomerModel(id=101, name="Alice Smith", email="alice@acmecorp.com", company="Acme Corp", phone="+1-555-0101"),
            CustomerModel(id=102, name="Bob Jones", email="bob@globex.com", company="Globex Corp", phone="+1-555-0102"),
            CustomerModel(id=103, name="Charlie Brown", email="charlie@stark.com", company="Stark Ind", phone="+1-555-0103"),
        ]
        db.add_all(sample_customers)
        db.commit()
        for c in sample_customers:
            db.refresh(c)
        return sample_customers
