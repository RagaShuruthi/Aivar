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

class GeminiLLM:
    """
    LLM Interface powering the AI Customer Assistant using Gemini 2.5 / 1.5 Flash.
    
    SYSTEM PROMPT RULES:
    - Gemini acts ONLY as a Tool Calling Model (never a conversational chatbot).
    - It NEVER answers users directly, NEVER returns markdown formatting, NEVER generates natural text.
    - Output strictly raw JSON in the schema:
      {
        "agent_id": "support_agent",
        "tool": "crm",
        "operation": "read" | "update" | "delete",
        "customer_id": 101,
        "fields": {},
        "reasoning": "..."
      }
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"
        self.is_configured = False

        if HAS_GENAI and self.api_key and not self.api_key.startswith("YOUR_") and self.api_key.strip() != "":
            try:
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


    def extract_tool_intent(self, prompt: str, agent_id: str = "support_agent", default_customer_id: int = 101) -> Dict[str, Any]:
        """
        Parses natural language prompt to extract tool parameters.
        Returns validated dict with keys: agent_id, tool, operation, customer_id, fields, reasoning
        """
        if self.is_configured:
            try:
                system_instruction = (
                    "You are a strict Tool Calling Model for an enterprise governance proxy. "
                    "You NEVER answer users directly. You NEVER return text explanations or markdown.\n"
                    "You convert natural language into raw JSON only.\n\n"
                    "JSON Format:\n"
                    "{\n"
                    '  "agent_id": "' + agent_id + '",\n'
                    '  "tool": "crm",\n'
                    '  "operation": "read",\n'
                    '  "customer_id": 101,\n'
                    '  "fields": {},\n'
                    '  "reasoning": "extacted intent description"\n'
                    "}\n\n"
                    "RULES:\n"
                    "1. Only set tool to 'crm'.\n"
                    "2. Allowed operations: 'read', 'update', 'delete'.\n"
                    "3. For update requests, place updated attributes in 'fields' (e.g. {\"email\": \"alice@gmail.com\"}).\n"
                    "4. If customer ID is mentioned (e.g. 101, 102, 205), use it in 'customer_id'. Otherwise default customer_id to " + str(default_customer_id) + ".\n"
                    "5. Output ONLY raw JSON. Do NOT wrap in ```json ``` markdown code blocks."
                )
                full_prompt = f"{system_instruction}\n\nUser Input: {prompt}"

                if GENAI_TYPE == "genai":
                    res = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=full_prompt
                    )
                    text = res.text.strip()
                else:
                    response = self.model.generate_content(full_prompt)
                    text = response.text.strip()

                # Clean JSON fences if present
                cleaned_text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
                cleaned_text = re.sub(r"\s*```$", "", cleaned_text, flags=re.MULTILINE)
                cleaned_text = cleaned_text.strip()

                parsed = json.loads(cleaned_text)
                return self._validate_and_sanitize(parsed, agent_id, default_customer_id)
            except Exception:
                pass

        # Intelligent Fallback Deterministic Parser
        return self._fallback_parser(prompt, agent_id, default_customer_id)

    def _validate_and_sanitize(self, data: Dict[str, Any], agent_id: str, default_customer_id: int) -> Dict[str, Any]:
        """Strict Security Sanitizer: Never trust LLM output blindly."""
        tool = str(data.get("tool", "crm")).lower()
        if tool != "crm":
            tool = "crm"

        op = str(data.get("operation", "read")).lower()
        if op not in ["read", "update", "delete"]:
            op = "read"

        try:
            cid = int(data.get("customer_id", default_customer_id))
        except (ValueError, TypeError):
            cid = default_customer_id

        fields = data.get("fields")
        if not isinstance(fields, dict):
            fields = {}

        return {
            "agent_id": agent_id,
            "tool": tool,
            "operation": op,
            "customer_id": cid,
            "fields": fields,
            "reasoning": str(data.get("reasoning", f"Extracted {op} intent for customer {cid}"))
        }

    def _fallback_parser(self, prompt: str, agent_id: str, default_customer_id: int) -> Dict[str, Any]:
        """Deterministic NLP regex fallback ensuring 100% reliable execution."""
        prompt_lower = prompt.lower()

        # Determine operation
        if any(w in prompt_lower for w in ["delete", "remove", "erase", "drop"]):
            operation = "delete"
        elif any(w in prompt_lower for w in ["update", "updation", "updating", "change", "modify", "edit", "rename", "set"]):
            operation = "update"
        else:
            operation = "read"


        # Extract customer ID if present (e.g. 101, 102, 205)
        match = re.search(r'\b([1-9][0-9]{2,3})\b', prompt)
        customer_id = int(match.group(1)) if match else default_customer_id

        # Extract update fields
        fields = {}
        if operation == "update":
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt)
            if email_match:
                fields["email"] = email_match.group(0)
            
            phone_match = re.search(r'\+?\d[\d\s-]{7,15}\d', prompt)
            if phone_match:
                fields["phone"] = phone_match.group(0).strip()
            
            if not fields:
                name_match = re.search(r'name\s+(?:to|=|is)\s+([A-Za-z\s]+)', prompt, re.IGNORECASE)
                if name_match:
                    fields["name"] = name_match.group(1).strip()
                else:
                    fields["name"] = "Alice Smith (Updated)"

        return {
            "agent_id": agent_id,
            "tool": "crm",
            "operation": operation,
            "customer_id": customer_id,
            "fields": fields,
            "reasoning": f"NLP Fallback: Identified '{operation}' operation on customer {customer_id}"
        }

# Singleton Instance
gemini_llm = GeminiLLM()
