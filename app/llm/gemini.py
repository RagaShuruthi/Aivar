import os
import re
import json
from typing import Dict, Any, Optional

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
    
    IMPORTANT SECURITY INVARIANT:
    This class ONLY parses natural language intent into structured tool call parameters.
    It NEVER touches databases or executes tool calls directly!
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"
        self.is_configured = False

        if HAS_GENAI and self.api_key:
            try:
                if GENAI_TYPE == "genai":
                    self.client = genai.Client(api_key=self.api_key)
                else:
                    genai_legacy.configure(api_key=self.api_key)
                    self.model = genai_legacy.GenerativeModel(self.model_name)
                self.is_configured = True
            except Exception:
                self.is_configured = False

    def extract_tool_intent(self, prompt: str, default_customer_id: int = 101) -> Dict[str, Any]:
        """
        Parses natural language prompt to extract tool parameters.
        Returns dict with: tool_name, operation, target_customer_id, payload_data
        """
        if self.is_configured:
            try:
                system_instruction = (
                    "You are an intent extractor for a CRM tool. "
                    "Analyze the user's prompt and extract structured JSON tool arguments.\n"
                    "Supported operations: 'read', 'update', 'delete'.\n"
                    "Tool name must always be 'crm'.\n"
                    "If a customer ID is mentioned (e.g. 101, 102), extract it as target_customer_id.\n"
                    "If no customer ID is specified, default target_customer_id to " + str(default_customer_id) + ".\n"
                    "Output STRICT raw JSON with keys: 'tool_name', 'operation', 'target_customer_id', 'payload_data'.\n"
                    "Do NOT include markdown formatting or extra text."
                )
                full_prompt = f"{system_instruction}\nUser Prompt: {prompt}"
                if GENAI_TYPE == "genai":
                    res = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=full_prompt
                    )
                    text = res.text.strip()
                else:
                    response = self.model.generate_content(full_prompt)
                    text = response.text.strip()
                # Clean JSON markdown fences if present
                cleaned_text = re.sub(r"^```json\s*", "", text)
                cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                parsed = json.loads(cleaned_text)
                return {
                    "tool_name": parsed.get("tool_name", "crm"),
                    "operation": parsed.get("operation", "read").lower(),
                    "target_customer_id": int(parsed.get("target_customer_id", default_customer_id)),
                    "payload_data": parsed.get("payload_data")
                }
            except Exception:
                pass

        # Intelligent Fallback Deterministic Parser (Runs if no API Key provided or network offline)
        return self._fallback_parser(prompt, default_customer_id)

    def _fallback_parser(self, prompt: str, default_customer_id: int) -> Dict[str, Any]:
        """Deterministic NLP regex fallback to guarantee zero-downtime demonstration."""
        prompt_lower = prompt.lower()

        # Determine operation
        if any(w in prompt_lower for w in ["delete", "remove", "erase", "drop"]):
            operation = "delete"
        elif any(w in prompt_lower for w in ["update", "change", "modify", "edit", "rename", "set"]):
            operation = "update"
        else:
            operation = "read"

        # Extract target customer ID if present (e.g. 101, 102, customer 103)
        match = re.search(r'\b(10[0-9]|1[1-9][0-9]|[2-9][0-9]{2})\b', prompt)
        target_id = int(match.group(1)) if match else default_customer_id

        # Extract update payload data if applicable
        payload_data = None
        if operation == "update":
            # Extract name if mentioned like 'name to Alice'
            name_match = re.search(r'name\s+(?:to|=|is)\s+([A-Za-z\s]+)', prompt, re.IGNORECASE)
            new_name = name_match.group(1).strip() if name_match else "Updated Customer Name"
            payload_data = {"name": new_name}

        return {
            "tool_name": "crm",
            "operation": operation,
            "target_customer_id": target_id,
            "payload_data": payload_data
        }

# Singleton instance
gemini_llm = GeminiLLM()
