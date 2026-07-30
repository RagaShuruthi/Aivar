import hashlib
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.models import UserModel

class AuthService:
    """Authentication and Role Management Service for Enterprise Users."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 for lightweight demonstration security."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """Verify plain password against stored hash."""
        return AuthService.hash_password(plain_password) == password_hash

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
        """Authenticate user by email and password."""
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
        """Fetch user record by email address."""
        return db.query(UserModel).filter(UserModel.email == email).first()

    @staticmethod
    def seed_initial_users(db: Session) -> List[UserModel]:
        """Seed SQLite database with pre-configured Enterprise Roles."""
        if db.query(UserModel).count() > 0:
            return db.query(UserModel).all()

        demo_users = [
            UserModel(
                name="Alice Smith",
                email="alice@enterprise.com",
                password_hash=AuthService.hash_password("password123"),
                role="support_agent",
                role_title="Customer Support",
                customer_id=101
            ),
            UserModel(
                name="Bob Jones",
                email="bob@enterprise.com",
                password_hash=AuthService.hash_password("password123"),
                role="admin_agent",
                role_title="CRM Administrator",
                customer_id=201
            ),
            UserModel(
                name="Charlie Brown",
                email="charlie@enterprise.com",
                password_hash=AuthService.hash_password("password123"),
                role="restricted_agent",
                role_title="Compliance Auditor",
                customer_id=301
            ),
        ]
        db.add_all(demo_users)
        db.commit()
        for u in demo_users:
            db.refresh(u)
        return demo_users
