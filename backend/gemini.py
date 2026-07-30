import os
import re
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Try modern google.genai SDK first, then legacy google.generativeai
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


class GeminiService:
    """
    Google Gemini 2.5 / 1.5 Flash Service.
    
    RESPONSIBILITIES:
    1. Intent Detection: Converts natural language into structured JSON tool requests.
    2. Response Generator: Converts CRM tool execution results / proxy denials into natural language.
    3. NEVER accesses CRM directly.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.0-flash"
        self.is_configured = False

        if HAS_GENAI and self.api_key:
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
            if not self.api_key:
                print("[INFO] No GEMINI_API_KEY found in .env. Running in Fallback Deterministic NLP mode.")

    def detect_intent(self, prompt: str, default_customer_id: int = 101, default_agent: str = "support_agent") -> Dict[str, Any]:
        """
        Step 1: Intent Detection.
        Converts natural language user prompt into structured JSON tool intent.
        """
        if self.is_configured:
            sys_prompt = f"""
            You are an AI Intent Extractor for an Enterprise CRM System.
            Convert the user's natural language input into JSON matching this EXACT schema:
            {{
                "agent": "{default_agent}",
                "tool": "crm",
                "operation": "read" | "update" | "delete",
                "customer_id": int,
                "field": string or null,
                "value": string or null
            }}
            Output ONLY valid JSON. No markdown ticks, no extra text.
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

        # Extract customer_id
        cid_match = re.search(r'\b(customer\s*|id\s*|#\s*)?(\d{3})\b', prompt_lower)
        customer_id = int(cid_match.group(2)) if cid_match else default_customer_id

        # Determine operation
        if any(w in prompt_lower for w in ["delete", "remove", "erase", "cancel"]):
            operation = "delete"
        elif any(w in prompt_lower for w in ["update", "change", "modify", "set"]):
            operation = "update"
        else:
            operation = "read"

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
            "tool": "crm",
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
        crm_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Step 2: Natural Language Response Generator.
        Translates raw CRM execution results or Permission Proxy denials into professional natural language responses.
        """
        if self.is_configured:
            try:
                nl_prompt = f"""
                You are a professional Enterprise AI Assistant.
                User Prompt: "{prompt}"
                Permission Proxy Result: Allowed={allowed}, Reason="{reason}"
                CRM Execution Data: {json.dumps(crm_data) if crm_data else "None"}

                Instructions:
                - If Allowed: Provide a polite, helpful summary of the CRM action outcome.
                - If Blocked: State clearly that the action was blocked by governance policy, explaining the reason professionally.
                - Keep response concise and business professional.
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
                if "deleted_customer_id" in crm_data:
                    return f"Customer record #{crm_data['deleted_customer_id']} has been permanently deleted from the CRM."
                return f"Customer profile for {crm_data.get('name', 'Customer')} (#{crm_data.get('id')}) retrieved successfully. Status: {crm_data.get('status')}, Email: {crm_data.get('email')}."
            return f"Action processed successfully: {reason}"
        else:
            return f"Request Blocked: {reason} No action has been performed on the CRM database."

# Singleton Gemini Service Instance
gemini_service = GeminiService()
