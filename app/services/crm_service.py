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
    def get_customer_by_name(db: Session, name: str) -> Optional[CustomerModel]:
        """Fetch a single customer by name (case-insensitive search)."""
        return db.query(CustomerModel).filter(CustomerModel.name.ilike(name.strip())).first()

    @staticmethod
    def validate_demo_login(db: Session, name: str, role_title: str) -> Optional[CustomerModel]:
        """
        Validates Demo Login:
        1. Name exists in mock CRM database
        2. Selected role matches user's assigned role
        """
        customer = CRMService.get_customer_by_name(db, name)
        if not customer:
            return None
        
        # Match display role title with stored role_title
        if customer.role_title.lower().strip() != role_title.lower().strip():
            return None

        return customer

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
        """Seeds SQLite database with 20 enterprise mock CRM profiles."""
        if db.query(CustomerModel).count() > 0:
            return db.query(CustomerModel).all()

        sample_customers = [
            # CRM Administrator (Read, Update, Delete) - admin_agent
            CustomerModel(id=101, name="Shuruthi", email="shuruthi@crm.com", company="Enterprise Core", phone="+1-555-0101", department="Executive Management", city="Boston", status="Active Admin", role="admin_agent", role_title="CRM Administrator"),
            CustomerModel(id=102, name="Kavin", email="kavin@crm.com", company="Tech Systems", phone="+1-555-0102", department="IT Infrastructure", city="Seattle", status="Active Admin", role="admin_agent", role_title="CRM Administrator"),
            CustomerModel(id=103, name="Sabari", email="sabari@crm.com", company="Data Ops", phone="+1-555-0103", department="Database Administration", city="Austin", status="Active Admin", role="admin_agent", role_title="CRM Administrator"),

            # Support Agent (Read, Update) - support_agent
            CustomerModel(id=104, name="Elakiya", email="elakiya@crm.com", company="Global Care", phone="+1-555-0104", department="Customer Operations", city="San Jose", status="Active Support", role="support_agent", role_title="Support Agent"),
            CustomerModel(id=105, name="Koushik", email="koushik@crm.com", company="Tech Care", phone="+1-555-0105", department="Technical Support", city="Chicago", status="Active Support", role="support_agent", role_title="Support Agent"),
            CustomerModel(id=106, name="Nithin", email="nithin@crm.com", company="Client Desk", phone="+1-555-0106", department="Client Success", city="New York", status="Active Support", role="support_agent", role_title="Support Agent"),
            CustomerModel(id=107, name="Raashmi", email="raashmi@crm.com", company="Service First", phone="+1-555-0107", department="Customer Care", city="Atlanta", status="Active Support", role="support_agent", role_title="Support Agent"),
            CustomerModel(id=108, name="Mousi", email="mousi@crm.com", company="Help Ops", phone="+1-555-0108", department="Help Desk", city="Denver", status="Active Support", role="support_agent", role_title="Support Agent"),

            # Read Only (Read Only) - restricted_agent
            CustomerModel(id=109, name="Ragul", email="ragul@crm.com", company="Legal Corp", phone="+1-555-0109", department="Compliance & Legal", city="San Francisco", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=110, name="Saran", email="saran@crm.com", company="Audit Systems", phone="+1-555-0110", department="Financial Audit", city="Dallas", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=111, name="Kanika", email="kanika@crm.com", company="Risk Corp", phone="+1-555-0111", department="Risk Analytics", city="Los Angeles", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=112, name="Malini", email="malini@crm.com", company="QA Global", phone="+1-555-0112", department="Quality Assurance", city="Miami", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=113, name="Malleshwar", email="malleshwar@crm.com", company="Audit Core", phone="+1-555-0113", department="Internal Audit", city="Phoenix", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=114, name="Kelwin", email="kelwin@crm.com", company="Sec Review", phone="+1-555-0114", department="Security Review", city="Portland", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=115, name="Vivna", email="vivna@crm.com", company="Reg Affairs", phone="+1-555-0115", department="Regulatory Affairs", city="San Diego", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=116, name="Dhanya", email="dhanya@crm.com", company="Data Gov", phone="+1-555-0116", department="Data Governance", city="Seattle", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=117, name="Sakthi", email="sakthi@crm.com", company="Report Corp", phone="+1-555-0117", department="Reporting", city="Houston", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=118, name="Santhosh", email="santhosh@crm.com", company="BI Insights", phone="+1-555-0118", department="Business Intelligence", city="Detroit", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=119, name="Rithish", email="rithish@crm.com", company="Product Research", phone="+1-555-0119", department="Product Research", city="Minneapolis", status="Read Only", role="restricted_agent", role_title="Read Only"),
            CustomerModel(id=120, name="Sanjay", email="sanjay@crm.com", company="Sec Ops", phone="+1-555-0120", department="Security Operations", city="Raleigh", status="Read Only", role="restricted_agent", role_title="Read Only"),
        ]
        db.add_all(sample_customers)
        db.commit()
        for c in sample_customers:
            db.refresh(c)
        return sample_customers
