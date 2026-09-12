import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LLMOrchestrator")

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

try:
    from groq import AsyncGroq
    HAS_GROQ_SDK = True
except ImportError:
    HAS_GROQ_SDK = False


class LLMOrchestrator:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()

        self.gemini_client = genai.Client(api_key=self.gemini_key) if (HAS_GEMINI_SDK and self.gemini_key) else None
        self.groq_client = AsyncGroq(api_key=self.groq_key) if (HAS_GROQ_SDK and self.groq_key) else None

    def intelligent_chunking(self, content: str, max_chars: int = 12000) -> str:
        if len(content) <= max_chars:
            return content
        head_len = int(max_chars * 0.6)
        tail_len = int(max_chars * 0.4)
        return content[:head_len] + "\n\n[...TRUNCATED...]\n\n" + content[-tail_len:]

    async def _call_gemini(self, prompt: str, schema_description: str) -> Optional[Dict[str, Any]]:
        if not self.gemini_client:
            raise ValueError("Gemini API key is missing or invalid.")

        system_instruction = f"Return strictly valid JSON adhering to schema: {schema_description}."
        
        # Explicitly disable AFC to remove SDK warnings
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"{system_instruction}\n\nInput:\n{prompt}",
                config=config
            )
        )
        return json.loads(response.text)

    async def _call_groq(self, prompt: str, schema_description: str) -> Optional[Dict[str, Any]]:
        if not self.groq_client:
            raise ValueError("Groq API key is missing or invalid.")

        response = await self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Extract JSON adhering strictly to: {schema_description}"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    async def extract_entity(self, raw_content: str, schema_description: str) -> Dict[str, Any]:
        processed_content = self.intelligent_chunking(raw_content)
        providers = [
            ("gemini", self._call_gemini),
            ("groq", self._call_groq)
        ]

        for provider_name, provider_func in providers:
            try:
                logger.info(f"Attempting LLM extraction via [{provider_name.upper()}] (Attempt 1)")
                result = await provider_func(processed_content, schema_description)
                if result:
                    logger.info(f"Successfully extracted data via [{provider_name.upper()}]")
                    return result
            except Exception as e:
                logger.error(f"Error executing [{provider_name.upper()}]: {e}")
                logger.warning(f"[{provider_name.upper()}] tier exhausted. Falling back...")

        logger.error("All LLM providers in fallback chain failed. Returning empty fallback.")
        return {}


if __name__ == "__main__":
    async def test_run():
        orchestrator = LLMOrchestrator()
        sample_text = "GraphOne pipeline test run."
        schema = "{'status': 'string'}"
        output = await orchestrator.extract_entity(sample_text, schema)
        print("\nFinal LLM Output:\n", json.dumps(output, indent=2))

    asyncio.run(test_run())
