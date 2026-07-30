import json
import os
from pathlib import Path
from typing import Dict, Optional
from app.models.permission import PermissionManifest, ToolCallPayload, PermissionDecision

class PermissionEngine:
    """
    Policy Decision Point (PDP).
    Evaluates tool invocation requests against JSON Permission Manifests and Session Contexts.
    """

    def __init__(self, manifests_dir: Optional[str] = None):
        if manifests_dir is None:
            # Default to app/manifests directory relative to project root
            base_dir = Path(__file__).resolve().parent.parent
            manifests_dir = str(base_dir / "manifests")
        self.manifests_dir = manifests_dir

    def load_manifest(self, agent_id: str) -> Optional[PermissionManifest]:
        """
        Dynamically loads and validates an agent's JSON manifest file.
        Example path: app/manifests/support_agent.json
        """
        file_path = os.path.join(self.manifests_dir, f"{agent_id}.json")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PermissionManifest(**data)
        except Exception as e:
            # Return None if JSON parsing or Pydantic validation fails
            return None

    def evaluate(self, payload: ToolCallPayload) -> PermissionDecision:
        """
        Evaluates a tool call request against manifest rules and session context.
        Returns a PermissionDecision object (allowed: bool, reason: str).
        """
        # Step 1: Verify Policy Manifest Existence
        manifest = self.load_manifest(payload.agent_id)
        if not manifest:
            return PermissionDecision(
                allowed=False,
                reason=f"Policy manifest for agent '{payload.agent_id}' does not exist or is invalid.",
                agent_id=payload.agent_id,
                tool_name=payload.tool_name,
                operation=payload.operation,
                target_customer_id=payload.target_customer_id
            )

        # Step 2: Verify Tool Name Authorization
        if payload.tool_name != manifest.tool_name:
            return PermissionDecision(
                allowed=False,
                reason=f"Agent '{payload.agent_id}' is not authorized to use tool '{payload.tool_name}'. Allowed tool: '{manifest.tool_name}'.",
                agent_id=payload.agent_id,
                tool_name=payload.tool_name,
                operation=payload.operation,
                target_customer_id=payload.target_customer_id
            )

        # Step 3: Verify Operation Whitelist (read / update / delete)
        if payload.operation not in manifest.allowed_operations:
            return PermissionDecision(
                allowed=False,
                reason=f"Operation '{payload.operation}' is BLOCKED. Agent '{payload.agent_id}' is only allowed: {manifest.allowed_operations}.",
                agent_id=payload.agent_id,
                tool_name=payload.tool_name,
                operation=payload.operation,
                target_customer_id=payload.target_customer_id
            )

        # Step 4: Evaluate Data Scope & Session Context Rules
        scope = manifest.data_scope

        if scope == "none":
            return PermissionDecision(
                allowed=False,
                reason=f"Data scope for agent '{payload.agent_id}' is set to 'none'. All data access is blocked.",
                agent_id=payload.agent_id,
                tool_name=payload.tool_name,
                operation=payload.operation,
                target_customer_id=payload.target_customer_id
            )

        if scope == "session_customer":
            session_customer_id = payload.session_context.customer_id
            if session_customer_id is None:
                return PermissionDecision(
                    allowed=False,
                    reason="Session Context Error: 'customer_id' is missing in session_context.",
                    agent_id=payload.agent_id,
                    tool_name=payload.tool_name,
                    operation=payload.operation,
                    target_customer_id=payload.target_customer_id
                )

            if payload.target_customer_id != session_customer_id:
                return PermissionDecision(
                    allowed=False,
                    reason=(
                        f"Data Scope Violation: Agent '{payload.agent_id}' is restricted to "
                        f"session customer ID {session_customer_id}, but requested target customer ID {payload.target_customer_id}."
                    ),
                    agent_id=payload.agent_id,
                    tool_name=payload.tool_name,
                    operation=payload.operation,
                    target_customer_id=payload.target_customer_id
                )

        # Step 5: All checks passed successfully!
        return PermissionDecision(
            allowed=True,
            reason=f"Access ALLOWED under manifest scope '{scope}' for operation '{payload.operation}'.",
            agent_id=payload.agent_id,
            tool_name=payload.tool_name,
            operation=payload.operation,
            target_customer_id=payload.target_customer_id
        )

# Global Engine Instance
permission_engine = PermissionEngine()
