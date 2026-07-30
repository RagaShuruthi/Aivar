from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from app.db.models import AuditLogModel, SecurityAlertModel
from app.models.permission import PermissionDecision

class AuditService:
    """Service layer managing Audit Log persistence and metrics computation."""

    @staticmethod
    def log_decision(db: Session, decision: PermissionDecision) -> AuditLogModel:
        """Persists a PermissionDecision outcome into the audit_logs table."""
        audit_entry = AuditLogModel(
            agent_id=decision.agent_id,
            tool_name=decision.tool_name,
            operation=decision.operation,
            target_customer_id=decision.target_customer_id,
            allowed=decision.allowed,
            reason=decision.reason
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

    @staticmethod
    def get_logs(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        allowed_filter: Optional[bool] = None,
        agent_id_filter: Optional[str] = None
    ) -> List[AuditLogModel]:
        """Fetches audit log entries with pagination and optional filters."""
        query = db.query(AuditLogModel)
        if allowed_filter is not None:
            query = query.filter(AuditLogModel.allowed == allowed_filter)
        if agent_id_filter:
            query = query.filter(AuditLogModel.agent_id == agent_id_filter)

        return query.order_by(AuditLogModel.timestamp.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_audit_statistics(db: Session) -> Dict[str, Any]:
        """Computes aggregate governance metrics for dashboard presentation."""
        total_requests = db.query(func.count(AuditLogModel.id)).scalar() or 0
        allowed_requests = db.query(func.count(AuditLogModel.id)).filter(AuditLogModel.allowed == True).scalar() or 0
        blocked_requests = db.query(func.count(AuditLogModel.id)).filter(AuditLogModel.allowed == False).scalar() or 0

        block_rate = (blocked_requests / total_requests * 100) if total_requests > 0 else 0.0
        active_alerts_count = db.query(func.count(SecurityAlertModel.id)).filter(SecurityAlertModel.is_active == True).scalar() or 0

        return {
            "total_requests": total_requests,
            "allowed_requests": allowed_requests,
            "blocked_requests": blocked_requests,
            "block_rate_percentage": round(block_rate, 2),
            "active_alerts_count": active_alerts_count
        }
