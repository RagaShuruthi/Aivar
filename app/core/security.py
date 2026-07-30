from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.db.models import AuditLogModel, SecurityAlertModel

class SecurityAlertService:
    """
    Automated Threat Detection Engine.
    Monitors audit logs for security policy violation spikes (>3 blocked requests).
    """
    BLOCKED_THRESHOLD: int = 3

    @classmethod
    def check_and_trigger_alert(cls, db: Session, agent_id: str) -> Optional[SecurityAlertModel]:
        """
        Evaluates an agent's historical blocked attempts.
        If blocked count > 3, generates and persists a SecurityAlert entry.
        """
        # Count total blocked actions for this agent
        blocked_count = db.query(func.count(AuditLogModel.id))\
            .filter(AuditLogModel.agent_id == agent_id, AuditLogModel.allowed == False)\
            .scalar() or 0

        # Check if threshold is breached (> 3)
        if blocked_count > cls.BLOCKED_THRESHOLD:
            # Check if an active alert already exists for this agent to prevent alert duplication
            existing_alert = db.query(SecurityAlertModel)\
                .filter(SecurityAlertModel.agent_id == agent_id, SecurityAlertModel.is_active == True)\
                .first()

            if not existing_alert:
                new_alert = SecurityAlertModel(
                    agent_id=agent_id,
                    reason=(
                        f"SECURITY ALERT: Agent '{agent_id}' exceeded maximum allowed security violation threshold! "
                        f"Detected {blocked_count} blocked attempts (Limit: {cls.BLOCKED_THRESHOLD})."
                    ),
                    total_blocked_count=blocked_count,
                    is_active=True
                )
                db.add(new_alert)
                db.commit()
                db.refresh(new_alert)
                return new_alert
            else:
                # Update existing alert with new count
                existing_alert.total_blocked_count = blocked_count
                db.commit()
                db.refresh(existing_alert)
                return existing_alert

        return None

    @staticmethod
    def get_alerts(db: Session, active_only: bool = False) -> List[SecurityAlertModel]:
        """Fetch security alert history for dashboard monitoring."""
        query = db.query(SecurityAlertModel)
        if active_only:
            query = query.filter(SecurityAlertModel.is_active == True)
        return query.order_by(SecurityAlertModel.timestamp.desc()).all()
