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
        self.model_name = "gemini-2.0-flash"
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
                print("[SUCCESS] Real Google Gemini LLM API activated successfully!")
            except Exception as e:
                self.is_configured = False
                print(f"[WARNING] Failed to initialize Gemini API: {e}")
        else:
            if not self.api_key or self.api_key.startswith("YOUR_"):
                print("[INFO] No valid GEMINI_API_KEY found in .env. Running in Fallback Deterministic NLP mode.")

    def detect_intent(self, prompt: str, default_customer_id: int = 101, default_agent: str = "support_agent") -> Dict[str, Any]:
        """
        Step 1: Intent Detection.
        Converts natural language user prompt into structured JSON tool intent or conversational chat.
        """
        prompt_clean = prompt.strip()

        # Direct check for conversational greetings / non-tool prompts
        conversational_triggers = {"hey", "hi", "hello", "greetings", "good morning", "good evening", "help", "who are you", "what can you do", "thanks", "thank you"}
        prompt_words = set(re.findall(r'\w+', prompt_clean.lower()))

        if prompt_words.intersection(conversational_triggers) and not any(w in prompt_clean.lower() for w in ["show", "view", "delete", "update", "customer", "profile", "record", "101", "102", "105"]):
            return {
                "agent": default_agent,
                "tool": "none",
                "operation": "chat",
                "customer_id": default_customer_id,
                "field": None,
                "value": None
            }

        if self.is_configured:
            sys_prompt = f"""
            You are an AI Intent Extractor for an Enterprise CRM System.
            Convert the user's natural language input into JSON matching this EXACT schema:
            {{
                "agent": "{default_agent}",
                "tool": "crm" | "none",
                "operation": "read" | "update" | "delete" | "chat",
                "customer_id": int,
                "field": string or null,
                "value": string or null
            }}
            Rules:
            - If user input is a greeting or general question (e.g. "hey", "hello", "how are you"), set operation to "chat" and tool to "none".
            - Output ONLY valid JSON. No markdown ticks, no extra text.
            Default customer_id if unspecified is {default_customer_id}.
            User Input: "{prompt}"
            """
            try:
                if GENAI_TYPE == "genai":
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=sys_prompt
                    )
                    raw_text = response.text
                else:
                    response = self.model.generate_content(sys_prompt)
                    raw_text = response.text

                cleaned = re.sub(r'```json\s*|\s*```', '', raw_text).strip()
                intent = json.loads(cleaned)
                return intent
            except Exception as e:
                print(f"[WARNING] Gemini Intent Extraction fallback: {e}")

        # Fallback Deterministic NLP Parser
        return self._fallback_intent_parser(prompt, default_customer_id, default_agent)

    def _fallback_intent_parser(self, prompt: str, default_customer_id: int, default_agent: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Check if conversational greeting
        conversational_triggers = ["hey", "hi", "hello", "greetings", "good morning", "good evening", "help", "who are you", "what can you do", "thanks", "thank you"]
        has_greeting = any(g in prompt_lower for g in conversational_triggers)
        has_crm_action = any(w in prompt_lower for w in ["show", "view", "read", "profile", "record", "details", "customer", "delete", "remove", "update", "updation", "updating", "change", "set", "edit", "101", "102", "105"])

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
        if any(w in prompt_lower for w in ["delete", "remove", "erase", "cancel"]):
            operation = "delete"
        elif any(w in prompt_lower for w in ["update", "updation", "updating", "change", "modify", "edit", "set"]):
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
            if "phone" in prompt_lower:
                field = "phone"
                phone_match = re.search(r'\b(\+?\d[-0-9\s]{7,15})\b', prompt)
                value = phone_match.group(1).strip() if phone_match else "+1-555-9999"
            elif "email" in prompt_lower:
                field = "email"
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt)
                value = email_match.group(0) if email_match else f"updated_{customer_id}@enterprise.com"
            elif "city" in prompt_lower:
                field = "city"
                value = "Chicago"
            elif "name" in prompt_lower:
                field = "name"
                value = "Updated Customer Name"
            else:
                field = "status"
                value = "Active VIP"

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
        if is_chat_only:
            return "Hello! I am your Enterprise AI CRM Assistant. How can I help you today? You can ask me to view customer profiles, update record details, or manage customer accounts depending on your role."

        if self.is_configured:
            try:
                nl_prompt = f"""
                You are a helpful, professional Enterprise CRM Virtual Assistant.
                User Prompt: "{prompt}"
                Action Result: Allowed={allowed}
                Technical Decision Details: "{reason}"
                Data Outcome: {json.dumps(crm_data) if crm_data else "None"}

                STRICT RESPONSE RULES:
                1. Respond in natural, polite, business-professional English.
                2. NEVER expose code variable names, technical agent IDs (e.g. 'support_agent', 'sales_agent'), raw JSON, or bracketed lists.
                3. If Allowed: State the result of the user's request clearly and politely.
                4. If Blocked: Explain in clear, simple human terms that the action is not permitted for their user role, without technical jargon.
                5. Do NOT include prefixes like "Request Blocked:" or "Permission Denied:". Speak directly to the user as a helpful virtual assistant.
                """
                if GENAI_TYPE == "genai":
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=nl_prompt
                    )
                    return response.text.strip()
                else:
                    response = self.model.generate_content(nl_prompt)
                    return response.text.strip()
            except Exception:
                pass

        # Fallback Natural Language Response Generation
        if allowed:
            if crm_data:
                if "deleted_customer_id" in crm_data or operation.lower() == "delete":
                    return f"Customer record #{crm_data.get('deleted_customer_id', crm_data.get('id'))} has been permanently deleted from the CRM."
                elif operation.lower() == "update":
                    return f"Customer profile for {crm_data.get('name', 'Customer')} (ID #{crm_data.get('id')}) has been updated successfully."
                return f"Customer profile for {crm_data.get('name', 'Customer')} (ID #{crm_data.get('id')}) retrieved successfully."
            return "Your request was processed successfully."
        else:
            return _humanize_denial_reason(reason, operation, target_customer_id)



# Singleton Gemini Service Instance
gemini_service = GeminiService()
