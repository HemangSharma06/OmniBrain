"""
backend/agents/guardrailsAgent.py

Simple GuardrailsAgent implementation performing input and output validations.
This is intentionally conservative and returns a structured validation result.
"""
import re
from typing import Dict


def _contains_secrets(text: str) -> bool:
    patterns = [r"api[_-]?key", r"secret", r"password", r"access[_-]?token", r"aws[_-]?secret", r"private[_-]?key"]
    txt = text.lower()
    return any(re.search(p, txt) for p in patterns)


def _looks_like_prompt_injection(text: str) -> bool:
    txt = text.lower()
    # Common bypass phrases
    phrases = [
        r"ignore (previous|earlier) instructions",
        r"disregard (previous|earlier|all) instructions",
        r"override (instructions|system prompt)",
        r"forget (your|the) (instructions|system prompt)",
        r"where is the system prompt",
        r"show me the system prompt",
        r"what are your instructions",
    ]
    for p in phrases:
        if re.search(p, txt):
            return True
    return False


def input_guardrail_check(payload: Dict) -> Dict:
    """
    Validate user input early in the graph.

    Returns a dict: {allowed: bool, reason, category, severity}
    """
    query = str(payload.get("query", "") or "").strip()

    if not query:
        return {"allowed": False, "reason": "Empty query provided.", "category": "input", "severity": "high"}

    if len(query) > 10000 or len(query.split()) > 3000:
        return {"allowed": False, "reason": "Query too large.", "category": "input", "severity": "high"}

    if _contains_secrets(query):
        return {"allowed": False, "reason": "Query appears to request secrets or credentials.", "category": "input", "severity": "high"}

    if _looks_like_prompt_injection(query):
        return {"allowed": False, "reason": "Prompt injection attempt detected.", "category": "input", "severity": "high"}

    # Low-confidence heuristics — mark as caution but allow
    if "password" in query.lower() or "api key" in query.lower():
        return {"allowed": False, "reason": "Potential secret-extraction request.", "category": "input", "severity": "high"}

    return {"allowed": True, "reason": "OK", "category": "input", "severity": "low"}

def output_guardrail_check(payload: Dict) -> Dict:
    """
    Validate a generated model answer before exposing to the user.
    Expects payload to contain 'answer' and optionally 'sources'/'documents'.
    """
    answer = str(payload.get("answer", "") or "")
    if not answer:
        return {"allowed": True, "reason": "No answer generated (empty).", "category": "output", "severity": "low"}

    if _contains_secrets(answer):
        return {"allowed": False, "reason": "Model output contains secrets or credentials.", "category": "output", "severity": "high"}

    if _looks_like_prompt_injection(answer):
        return {"allowed": False, "reason": "Model output reveals internal instructions.", "category": "output", "severity": "high"}

    # Additional heuristics — e.g., do not allow model to return raw system prompts
    if "system prompt" in answer.lower() or "developer instruction" in answer.lower():
        return {"allowed": False, "reason": "Model attempted to reveal system instructions.", "category": "output", "severity": "high"}

    return {"allowed": True, "reason": "OK", "category": "output", "severity": "low"}
