"""
Unified LLM Service for JobPilot AI.
Features resilient automatic provider switching and failover between Google Gemini, OpenAI, and Local modes.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Track temporary provider failures so repeated calls don't waste time on a broken service
_provider_backoff: Dict[str, float] = {}


def _call_gemini(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> Tuple[bool, str]:
    """Call Google Gemini API via official REST interface."""
    api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
    if not api_key:
        return False, "Gemini API key is missing"

    # Try configured model, then fallback models if specific one is unavailable
    candidate_models = [
        settings.GEMINI_MODEL,
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash",
    ]
    seen = set()
    models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

    contents = []
    if system_instruction:
        contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {system_instruction}"}]})
        contents.append({"role": "model", "parts": [{"text": "Understood. I will follow your instructions."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    last_error = ""
    for model_name in models_to_try:
        url = f"{GEMINI_API_URL.format(model=model_name)}?key={api_key}"
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload)

            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return True, parts[0]["text"].strip()
                return False, "Empty response from Gemini"

            # Parse error message
            error_data = res.json().get("error", {})
            last_error = f"Gemini {model_name} HTTP {res.status_code}: {error_data.get('message', res.text[:200])}"
            logger.warning(last_error)

            # If it's a 404 (model not available in region/tier), try next candidate model
            if res.status_code == 404:
                continue

            # If it's 429, 503, 403, or 401, fail out to trigger secondary provider
            break

        except Exception as e:
            last_error = f"Gemini connection error: {e}"
            logger.warning(last_error)
            break

    return False, last_error


def _call_openai(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> Tuple[bool, str]:
    """Call OpenAI Chat Completions API via official REST interface."""
    api_key = settings.OPENAI_API_KEY.strip() if settings.OPENAI_API_KEY else ""
    if not api_key:
        return False, "OpenAI API key is missing"

    candidate_models = [
        settings.OPENAI_MODEL,
        "gpt-4o-mini",
        "gpt-5-nano",
        "gpt-3.5-turbo",
    ]
    seen = set()
    models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error = ""
    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(OPENAI_API_URL, headers=headers, json=payload)

            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    return True, text.strip()
                return False, "Empty choices from OpenAI"

            error_data = res.json().get("error", {})
            last_error = f"OpenAI {model_name} HTTP {res.status_code}: {error_data.get('message', res.text[:200])}"
            logger.warning(last_error)

            # If model is not accessible to this project/tier, try next model
            if "does not have access to model" in last_error or res.status_code == 404:
                continue

            break

        except Exception as e:
            last_error = f"OpenAI connection error: {e}"
            logger.warning(last_error)
            break

    return False, last_error


class LLMService:
    """Unified LLM orchestrator with automatic provider failover."""

    def __init__(self):
        self.settings = get_settings()

    def _determine_provider_chain(self) -> List[str]:
        """
        Determine the order of LLM providers to try.
        Options: 'auto', 'gemini', 'openai', 'local'
        """
        mode = (self.settings.LLM_PROVIDER or "auto").lower()

        if mode == "local":
            return ["local"]
        elif mode == "gemini":
            return ["gemini", "openai"] if self.settings.LLM_AUTO_FALLBACK else ["gemini"]
        elif mode == "openai":
            return ["openai", "gemini"] if self.settings.LLM_AUTO_FALLBACK else ["openai"]
        else:  # "auto"
            # Default order: Try Gemini first, then OpenAI
            return ["gemini", "openai", "local"]

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> Dict[str, Any]:
        """
        Generate text using primary provider with automatic failover to backup provider.
        Returns dict with: text, provider_used, failover_occurred, error (if any).
        """
        chain = self._determine_provider_chain()
        attempted_providers = []

        for provider in chain:
            if provider == "local":
                attempted_providers.append("local")
                return {
                    "text": self._local_fallback_text(prompt),
                    "provider_used": "local",
                    "failover_occurred": len(attempted_providers) > 1,
                    "attempted": attempted_providers,
                }

            if provider == "gemini":
                attempted_providers.append("gemini")
                success, output = _call_gemini(
                    prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if success:
                    if len(attempted_providers) > 1:
                        logger.info(f"LLM request succeeded via failover to Gemini (attempted: {attempted_providers})")
                    return {
                        "text": output,
                        "provider_used": "gemini",
                        "failover_occurred": len(attempted_providers) > 1,
                        "attempted": attempted_providers,
                    }
                else:
                    logger.warning(f"Gemini call failed ({output}). Triggering automatic failover...")

            elif provider == "openai":
                attempted_providers.append("openai")
                success, output = _call_openai(
                    prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if success:
                    if len(attempted_providers) > 1:
                        logger.info(f"LLM request succeeded via failover to OpenAI (attempted: {attempted_providers})")
                    return {
                        "text": output,
                        "provider_used": "openai",
                        "failover_occurred": len(attempted_providers) > 1,
                        "attempted": attempted_providers,
                    }
                else:
                    logger.warning(f"OpenAI call failed ({output}). Triggering automatic failover...")

        # If all external LLMs failed, use deterministic local fallback
        logger.warning(f"All external LLM providers failed ({attempted_providers}). Using graceful local fallback.")
        return {
            "text": self._local_fallback_text(prompt),
            "provider_used": "local_fallback",
            "failover_occurred": True,
            "attempted": attempted_providers,
        }

    def _local_fallback_text(self, prompt: str) -> str:
        """Graceful local text generator when external APIs are unavailable/exhausted."""
        prompt_lower = prompt.lower()
        if "summary" in prompt_lower:
            return (
                "Results-driven professional with demonstrated competence in software engineering, "
                "problem-solving, and continuous learning. Passionate about delivering scalable solutions."
            )
        elif "cover letter" in prompt_lower:
            return (
                "Dear Hiring Team,\n\n"
                "I am writing to express my enthusiastic interest in this position. With my background in technology, "
                "collaboration, and technical problem-solving, I am confident in my ability to contribute effectively "
                "to your organization.\n\nThank you for considering my application."
            )
        elif "interview" in prompt_lower:
            return (
                "1. Can you describe a challenging technical project you delivered recently?\n"
                "2. How do you approach debugging and problem isolation in production?\n"
                "3. What strategies do you use to quickly adapt to new tools and frameworks?"
            )
        return "Processed locally via rule-based assistant."

    def enhance_resume_summary(
        self,
        current_summary: str,
        skills: Optional[List[str]] = None,
        target_role: Optional[str] = None,
    ) -> str:
        """Generate an enhanced, impactful resume summary."""
        skills_str = ", ".join(skills[:8]) if skills else "relevant industry skills"
        role_str = target_role or "target industry roles"

        prompt = (
            f"Rewrite the following candidate resume summary to be professional, compelling, and ATS-optimized.\n"
            f"Target Role: {role_str}\n"
            f"Key Skills: {skills_str}\n"
            f"Current Summary:\n\"\"\"{current_summary}\"\"\"\n\n"
            f"Return ONLY the enhanced summary in 3-4 impactful sentences. Do not include markdown preamble."
        )
        res = self.generate_text(
            prompt,
            system_instruction="You are an expert executive resume writer and career coach.",
            temperature=0.7,
            max_tokens=300,
        )
        return res["text"]

    def generate_cover_letter(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str,
        job_description: str,
        candidate_skills: Optional[List[str]] = None,
    ) -> str:
        """Generate a tailored cover letter matching candidate profile to job description."""
        skills_str = ", ".join(candidate_skills[:8]) if candidate_skills else "software and technical skills"
        prompt = (
            f"Write a personalized, compelling cover letter from {candidate_name} applying for the "
            f"'{job_title}' position at '{company_name}'.\n\n"
            f"Candidate Skills: {skills_str}\n"
            f"Job Description excerpt:\n\"\"\"{job_description[:1200]}\"\"\"\n\n"
            f"Guidelines:\n"
            f"- Professional, confident tone\n"
            f"- Connect candidate skills directly to the role requirements\n"
            f"- 3 to 4 paragraphs\n"
            f"- Do not include placeholders like '[Insert Date]'."
        )
        res = self.generate_text(
            prompt,
            system_instruction="You are a professional hiring manager and career strategist.",
            temperature=0.7,
            max_tokens=800,
        )
        return res["text"]

    def get_status(self) -> Dict[str, Any]:
        """Return configuration and health status of all LLM providers."""
        return {
            "mode": self.settings.LLM_PROVIDER,
            "auto_fallback": self.settings.LLM_AUTO_FALLBACK,
            "gemini_configured": bool(self.settings.GEMINI_API_KEY),
            "gemini_model": self.settings.GEMINI_MODEL,
            "openai_configured": bool(self.settings.OPENAI_API_KEY),
            "openai_model": self.settings.OPENAI_MODEL,
            "provider_chain": self._determine_provider_chain(),
        }


llm_service = LLMService()
