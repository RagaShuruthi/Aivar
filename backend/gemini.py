import os
import re
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

HAS_GENAI = False
GENAI_TYPE = None

try:
    from google import genai
    HAS_GENAI = True
    GENAI_TYPE = "genai"
except ImportError:
    try:
        import google.generativeai as genai_legacy
        HAS_GENAI = True
        GENAI_TYPE = "legacy"
    except ImportError:
        HAS_GENAI = False


def _humanize_denial_reason(reason: str, operation: str = "read", customer_id: Optional[int] = None) -> str:
    """Converts internal policy denial reasons into polite, natural conversational text."""
    is_security_alert = "SECURITY ALERT" in reason or "probing" in reason
    
    if "Outside session scope" in reason or "session_customer_only" in reason or "restricted to session customer" in reason:
        base_msg = f"You are only authorized to access your own customer profile. Access to Customer #{customer_id} is restricted."
    elif operation.lower() == "delete":
        base_msg = "You do not have permission to delete customer records. This action requires administrative privileges."
    elif operation.lower() == "update":
        base_msg = "You do not have permission to modify customer details for this account."
    else:
        base_msg = "You do not have permission to execute this action under your current user role."

    if is_security_alert:
        base_msg += " Multiple unauthorized attempts have been recorded for security governance."

    return f"{base_msg} No changes were made to the CRM database."


class GeminiService:
    """
    Google Gemini Service.
    
    RESPONSIBILITIES:
    1. Intent Detection: Converts natural language into structured JSON tool requests or conversational chat.
    2. Response Generator: Converts CRM tool execution results / proxy denials into natural language.
    3. NEVER accesses CRM directly.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"
        self.fallback_model_name = "gemini-2.0-flash"
        self.is_configured = False

        if HAS_GENAI and self.api_key and not self.api_key.startswith("YOUR_") and self.api_key.strip() != "":
            try:
                os.environ["GOOGLE_API_KEY"] = self.api_key
                if GENAI_TYPE == "genai":
                    self.client = genai.Client(api_key=self.api_key)
                else:
                    genai_legacy.configure(api_key=self.api_key)
                    self.model = genai_legacy.GenerativeModel(self.model_name)
                self.is_configured = True
                print(f"[SUCCESS] Real Google Gemini LLM API activated ({self.model_name})!")
            except Exception as e:
                self.is_configured = False
                print(f"[WARNING] Failed to initialize Gemini API: {e}")
        else:
            if not self.api_key or self.api_key.startswith("YOUR_"):
                print("[INFO] No valid GEMINI_API_KEY found in .env. Running in Fallback Deterministic Engine mode.")

    def _call_gemini_llm(self, prompt_text: str) -> Optional[str]:
        """Executes LLM request with automatic model fallback and strict 2.0s latency cap."""
        if not self.is_configured:
            return None

        import concurrent.futures

        def _fetch():
            models_to_try = [self.model_name, self.fallback_model_name]
            for m_name in models_to_try:
                try:
                    if GENAI_TYPE == "genai":
                        res = self.client.models.generate_content(
                            model=m_name,
                            contents=prompt_text
                        )
                        return res.text.strip()
                    else:
                        legacy_model = genai_legacy.GenerativeModel(m_name)
                        res = legacy_model.generate_content(prompt_text)
                        return res.text.strip()
                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        continue
                    else:
                        break
            return None

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_fetch)
                return future.result(timeout=2.0)
        except Exception:
            # Latency cap exceeded or error: fail fast to instant local response engine
            return None


    def detect_intent(self, prompt: str, default_customer_id: int = 101, default_agent: str = "support_agent") -> Dict[str, Any]:
        """
        Step 1: Ultra-Fast High-Speed Intent Detection.
        Converts natural language user prompt into structured JSON tool intent instantly (< 1ms).
        """
        return self._fallback_intent_parser(prompt, default_customer_id, default_agent)


    def _fallback_intent_parser(self, prompt: str, default_customer_id: int, default_agent: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Audit History Check
        if any(trig in prompt_lower for trig in ["what was updated", "show history", "recent changes", "audit logs", "audit trail", "who modified", "what changed"]):
            return {
                "agent": default_agent,
                "tool": "audit_service",
                "operation": "audit",
                "customer_id": default_customer_id,
                "field": None,
                "value": None
            }

        # Permission Question Check
        if any(trig in prompt_lower for trig in ["what can i do", "my permissions", "am i allowed", "my scope", "what operations"]):
            return {
                "agent": default_agent,
                "tool": "permission_engine",
                "operation": "permission_info",
                "customer_id": default_customer_id,
                "field": None,
                "value": None
            }

        # Conversational Greeting Check
        conversational_triggers = ["hey", "hi", "hello", "greetings", "good morning", "good evening", "help", "who are you", "what can you do", "thanks", "thank you"]
        has_greeting = any(g in prompt_lower for g in conversational_triggers)
        has_crm_action = any(w in prompt_lower for w in ["show", "view", "read", "profile", "record", "details", "customer", "delete", "remove", "update", "updation", "updating", "change", "set", "edit", "create", "add", "101", "102", "105"])

        if has_greeting and not has_crm_action:
            return {
                "agent": default_agent,
                "tool": "none",
                "operation": "chat",
                "customer_id": default_customer_id,
                "field": None,
                "value": None
            }

        # Extract customer_id
        cid_match = re.search(r'\b(customer\s*|id\s*|#\s*)?(\d{3})\b', prompt_lower)
        customer_id = int(cid_match.group(2)) if cid_match else default_customer_id

        # Determine operation
        is_read_intent = any(w in prompt_lower for w in ["show", "view", "read", "display", "see", "profile", "record", "details", "updated data", "updated profile"])

        if is_read_intent:
            operation = "read"
        elif any(w in prompt_lower for w in ["create", "add new", "new customer", "register customer"]):
            operation = "create"
        elif any(w in prompt_lower for w in ["delete", "remove", "erase", "cancel"]):
            operation = "delete"
        elif any(re.search(r'\b' + re.escape(w) + r'\b', prompt_lower) for w in ["update", "updation", "updating", "change", "modify", "edit", "set"]):
            operation = "update"
        elif has_crm_action or cid_match:
            operation = "read"
        else:
            operation = "chat"


        tool = "none" if operation == "chat" else "crm"

        # Determine field & value for update
        field = None
        value = None

        if operation == "update":
            # Extract explicit field if specified
            if "phone" in prompt_lower:
                field = "phone"
                phone_match = re.search(r'\b(\+?\d[-0-9\s]{7,15})\b', prompt)
                value = phone_match.group(1).strip() if phone_match else None
            elif "email" in prompt_lower:
                field = "email"
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt)
                value = email_match.group(0) if email_match else None
            elif "city" in prompt_lower:
                field = "city"
                city_match = re.search(r'city\s+(?:to|=|is)\s+([A-Za-z\s]+)', prompt, re.IGNORECASE)
                value = city_match.group(1).strip() if city_match else None
            elif "name" in prompt_lower:
                field = "name"
                name_match = re.search(r'name\s+(?:to|=|is)\s+([A-Za-z\s]+)', prompt, re.IGNORECASE)
                value = name_match.group(1).strip() if name_match else None

        return {
            "agent": default_agent,
            "tool": tool,
            "operation": operation,
            "customer_id": customer_id,
            "field": field,
            "value": value
        }

    def generate_nl_response(
        self,
        prompt: str,
        allowed: bool,
        reason: str,
        crm_data: Optional[Dict[str, Any]] = None,
        is_chat_only: bool = False,
        operation: str = "read",
        target_customer_id: Optional[int] = None
    ) -> str:
        """
        Step 2: Natural Language Response Generator.
        Translates raw CRM execution results or Permission Proxy denials into professional natural language responses.
        """
        prompt_lower = prompt.lower().strip()

        if self.is_configured:
            if is_chat_only:
                nl_prompt = f"""
                You are a helpful, professional Enterprise CRM Virtual Assistant.
                User Input: "{prompt}"
                
                Respond naturally, politely, and contextually to the user's conversational message (e.g. greetings, acknowledgments like "okay done", "thanks", "got it", "great"). Keep response concise, friendly, and business professional.
                """
            else:
                nl_prompt = f"""
                You are a helpful, professional Enterprise CRM Virtual Assistant.
                User Prompt: "{prompt}"
                Action Result: Allowed={allowed}
                Technical Decision Details: "{reason}"
                Data Outcome: {json.dumps(crm_data) if crm_data else "None"}

                STRICT RESPONSE RULES:
                1. Respond in natural, polite, business-professional English.
                2. NEVER expose code variable names, technical agent IDs (e.g. 'support_agent', 'sales_agent'), raw JSON, or bracketed lists.
                3. If Allowed: State the result of the user's request clearly and politely. Include the retrieved customer details if relevant.
                4. If Blocked: Explain in clear, simple human terms that the action is not permitted for their user role, without technical jargon.
                5. Do NOT include prefixes like "Request Blocked:" or "Permission Denied:". Speak directly to the user as a helpful virtual assistant.
                """
            llm_text = self._call_gemini_llm(nl_prompt)
            if llm_text:
                return llm_text

        # Fallback Natural Language Response Generation for Chat / Conversational Queries
        if is_chat_only:
            if any(w in prompt_lower for w in ["okay", "done", "got it", "thanks", "thank you", "great", "perfect", "alright", "cool"]):
                return "You're welcome! Let me know if you need to view, update, or manage any customer records."
            return "Hello! I am your Enterprise AI CRM Assistant. How can I help you today? You can ask me to view customer profiles, update record details, or check audit history depending on your user role."

        # Fallback Natural Language Response Generation for CRM Actions
        if allowed:
            if crm_data:
                if "summary" in crm_data:
                    return crm_data["summary"]
                elif "permissions" in crm_data:
                    return reason
                elif "deleted_customer_id" in crm_data or operation.lower() == "delete":
                    return f"Customer record #{crm_data.get('deleted_customer_id', crm_data.get('id'))} has been permanently deleted from the CRM."
                elif operation.lower() == "update":
                    return f"Customer profile for {crm_data.get('name', 'Customer')} (ID #{crm_data.get('id')}) has been updated successfully."
                elif "name" in crm_data:
                    return f"Customer profile for {crm_data.get('name')} (ID #{crm_data.get('id')}) retrieved successfully. Status: {crm_data.get('status')}, Email: {crm_data.get('email')}."
            return f"Your request for customer #{target_customer_id or 101} was processed successfully."
        else:
            return _humanize_denial_reason(reason, operation, target_customer_id)




# Singleton Gemini Service Instance
gemini_service = GeminiService()
