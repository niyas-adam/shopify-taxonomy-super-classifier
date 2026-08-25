from typing import Dict, Optional
from django.conf import settings


try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMClassifier:
    def __init__(self):
        config = getattr(settings, 'CLASSIFICATION_CONFIG', {})
        self.provider = config.get('llm_provider', 'groq')
        self.api_key = config.get('llm_api_key', '')
        self.model = config.get('llm_model', '')

    def classify(self, product_text: str, candidates: list) -> Optional[Dict]:
        if not self.api_key:
            return None
        prompt = self._build_prompt(product_text, candidates)
        try:
            if self.provider == 'groq' and GROQ_AVAILABLE:
                return self._classify_with_groq(prompt)
            elif self.provider == 'gemini' and GEMINI_AVAILABLE:
                return self._classify_with_gemini(prompt)
            elif self.provider == 'openai' and OPENAI_AVAILABLE:
                return self._classify_with_openai(prompt)
        except Exception:
            return None
        return None

    def _build_prompt(self, product_text: str, candidates: list) -> str:
        candidate_list = '\n'.join([
            f"- {c.get('name', '')} ({c.get('full_path', '')})"
            for c in candidates[:10]
        ])
        return f"""Classify this product into one of the Shopify categories:

Product: {product_text}

Candidate categories:
{candidate_list}

Return JSON: {{"category": "name", "confidence": 0.0-1.0, "reason": "explanation"}}"""

    def _classify_with_groq(self, prompt: str) -> Optional[Dict]:
        if not GROQ_AVAILABLE:
            return None
        client = groq.Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model or 'llama3-8b-8192',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.1,
        )
        import json
        return json.loads(response.choices[0].message.content)

    def _classify_with_gemini(self, prompt: str) -> Optional[Dict]:
        if not GEMINI_AVAILABLE:
            return None
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model or 'gemini-pro')
        response = model.generate_content(prompt)
        import json
        return json.loads(response.text)

    def _classify_with_openai(self, prompt: str) -> Optional[Dict]:
        if not OPENAI_AVAILABLE:
            return None
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model or 'gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.1,
        )
        import json
        return json.loads(response.choices[0].message.content)