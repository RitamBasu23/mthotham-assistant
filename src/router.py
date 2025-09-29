# src/router.py

def route_intent(question: str) -> str:
    """Very simple rule-based intent router.
    Expands later if needed, but avoids extra LLM calls for now.
    """
    q = question.lower()

    if "snow" in q or "weather" in q or "conditions" in q:
        return "weather"
    elif "ski pass" in q or "lift ticket" in q or "pass" in q:
        return "ski_pass"
    elif "accommodation" in q or "hotel" in q or "lodge" in q:
        return "accommodation"
    elif "transport" in q or "bus" in q or "shuttle" in q:
        return "transport"
    elif "food" in q or "dining" in q or "restaurant" in q:
        return "dining"
    elif "safety" in q or "guidelines" in q or "rules" in q:
        return "safety"
    else:
        return "general"
