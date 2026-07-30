import json
import os
from typing import Dict, Any, Tuple
from backend.crm import crm_db
from backend.logger import audit_logger

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")

class PermissionProxy:
    """
    Core Permission Proxy Policy Decision Point (PDP).
    
    PROBLEM STATEMENT PS-2.2 COMPLIANCE:
    1. Wrapper around sample toolset (Mock CRM API with read, write/update, delete).
    2. Permission manifest per agent: agent_id, tool_name, allowed_operations, data_scope.
    3. Evaluates every tool call against permission manifest before forwarding to CRM.
    4. Violations are BLOCKED and LOGGED with reason; within-scope calls forwarded transparently.
    5. Session context injector: evaluates dynamic data_scope rules (customer_id == session_customer_id).
    6. BONUS FEATURE: Real-time security alert for potential probing behavior (3+ blocks per session).
    """

    def __init__(self, manifest_path: str = MANIFEST_PATH):
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Permission manifest missing at: {self.manifest_path}")
        with open(self.manifest_path, "r") as f:
            return json.load(f)

    def reload_manifest(self):
        """Allows hot-reloading policy manifest rules."""
        self.manifest = self._load_manifest()

    def evaluate_and_execute(
        self,
        user: str,
        agent: str,
        tool: str,
        operation: str,
        customer_id: int,
        field: str = None,
        value: str = None,
        session_customer_id: int = 101
    ) -> Tuple[bool, str, Any, int]:
        """
        Evaluates tool call request against permission manifest and executes CRM operation if authorized.
        Returns: (allowed, reason, result_data, audit_log_id)
        """
        # Reload manifest dynamically to support live policy edits
        self.reload_manifest()

        agent_policy = self.manifest.get(agent)
        if not agent_policy:
            reason = f"Permission Denied: Agent '{agent}' is not registered in permission manifest."
            audit_id = audit_logger.log(user, agent, operation, customer_id, False, reason)
            return False, reason, None, audit_id

        # Check tool match
        policy_tool = agent_policy.get("tool", "crm")
        if tool != policy_tool:
            reason = f"Permission Denied: Agent '{agent}' is not authorized to access tool '{tool}'."
            audit_id = audit_logger.log(user, agent, operation, customer_id, False, reason)
            return False, reason, None, audit_id

        # Check allowed operations
        allowed_ops = agent_policy.get("allowed_operations", [])
        normalized_op = operation.lower()
        if normalized_op not in [op.lower() for op in allowed_ops]:
            reason = f"Permission Denied: Agent '{agent}' is NOT permitted to execute '{operation}' on '{tool}'. Allowed operations: {allowed_ops}."
            
            # Check Bonus Feature: Real-time Probing Threat Detection
            audit_id = audit_logger.log(user, agent, operation, customer_id, False, reason)
            blocks_count = audit_logger.count_session_blocks(user, agent)
            if blocks_count >= 3:
                reason += f" [SECURITY ALERT]: Potential probing behavior detected! User/Agent '{user}' ({agent}) has exceeded {blocks_count} failed security checks in this session."
            
            return False, reason, None, audit_id

        # Check data scope (customer_id must equal session_customer_id for session_customer_only)
        scope = agent_policy.get("scope", "session_customer_only")
        if scope == "session_customer_only" and customer_id != session_customer_id:
            reason = f"Permission Denied: Outside session scope. Agent '{agent}' scope is restricted to session customer #{session_customer_id}. Cannot access customer #{customer_id}."
            
            # Check Bonus Feature: Real-time Probing Threat Detection
            audit_id = audit_logger.log(user, agent, operation, customer_id, False, reason)
            blocks_count = audit_logger.count_session_blocks(user, agent)
            if blocks_count >= 3:
                reason += f" [SECURITY ALERT]: Potential probing behavior detected! User/Agent '{user}' ({agent}) has exceeded {blocks_count} failed security checks in this session."
            
            return False, reason, None, audit_id

        # If AUTHORIZED -> Execute downstream CRM operation
        result_data = None
        if normalized_op in ["read", "read_profile"]:
            result_data = crm_db.read_customer(customer_id)
            if not result_data:
                reason = f"Operation Allowed, but Customer #{customer_id} was not found in CRM database."
                audit_id = audit_logger.log(user, agent, operation, customer_id, True, reason)
                return True, reason, None, audit_id
            reason = f"Operation Allowed: Read profile for Customer #{customer_id}."

        elif normalized_op in ["update", "write"]:
            if not field or not value:
                field = field or "phone"
                value = value or "+1-555-9999"
            result_data = crm_db.update_customer(customer_id, field, value)
            reason = f"Operation Allowed: Updated '{field}' to '{value}' for Customer #{customer_id}."

        elif normalized_op == "delete":
            success = crm_db.delete_customer(customer_id)
            if success:
                result_data = {"deleted_customer_id": customer_id, "status": "Deleted"}
                reason = f"Operation Allowed: Permanently deleted Customer #{customer_id}."
            else:
                reason = f"Operation Allowed, but Customer #{customer_id} was not found in CRM database."
                audit_id = audit_logger.log(user, agent, operation, customer_id, True, reason)
                return True, reason, None, audit_id

        audit_id = audit_logger.log(user, agent, operation, customer_id, True, reason)
        return True, reason, result_data, audit_id

# Instantiated Singleton PermissionProxy
permission_proxy = PermissionProxy()
