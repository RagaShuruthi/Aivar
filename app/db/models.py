from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.db.session import Base

class CustomerModel(Base):
    """SQLAlchemy ORM model representing CRM Customer records in SQLite."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    company = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    department = Column(String(100), nullable=True, default="Enterprise Sales")
    city = Column(String(100), nullable=True, default="San Francisco")
    status = Column(String(50), nullable=True, default="Active VIP")
    role = Column(String(50), nullable=True, default="support_agent")
    role_title = Column(String(100), nullable=True, default="Support Agent")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', role='{self.role}')>"


class AuditLogModel(Base):
    """SQLAlchemy ORM model for storing immutable request audit trails."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    agent_id = Column(String(50), index=True, nullable=False)
    tool_name = Column(String(50), nullable=False)
    operation = Column(String(20), nullable=False)  # read, update, delete
    target_customer_id = Column(Integer, nullable=True, index=True)
    allowed = Column(Boolean, nullable=False, index=True)  # True = ALLOWED, False = BLOCKED
    reason = Column(Text, nullable=False)

    def __repr__(self):
        status = "ALLOWED" if self.allowed else "BLOCKED"
        return f"<AuditLog(agent='{self.agent_id}', op='{self.operation}', status='{status}')>"


class SecurityAlertModel(Base):
    """SQLAlchemy ORM model for tracking security alerts generated when agents violate permissions repeatedly."""
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    agent_id = Column(String(50), index=True, nullable=False)
    reason = Column(Text, nullable=False)
    total_blocked_count = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<SecurityAlert(agent='{self.agent_id}', count={self.total_blocked_count})>"


class UserModel(Base):
    """SQLAlchemy ORM model for enterprise user authentication and role mapping."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # support_agent, admin_agent, restricted_agent
    role_title = Column(String(100), nullable=False)  # Customer Support, CRM Administrator, Compliance Auditor
    customer_id = Column(Integer, nullable=False)  # Associated session customer ID (e.g. 101, 201, 301)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}', customer_id={self.customer_id})>"

