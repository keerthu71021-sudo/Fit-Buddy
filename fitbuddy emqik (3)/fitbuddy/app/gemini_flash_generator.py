import json

from .ai_common import generate_gemini_text
from .config import TIP_MODEL


def _extract_json(text: str) -> dict:
    """Parse JSON even if the model wrapped it in markdown fences or extra prose."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in Gemini response")
    return json.loads(text[start : end + 1])


def generate_nutrition(profile: dict) -> dict:
    raw_response = generate_gemini_text(
        TIP_MODEL,
        f"Create concise, actionable nutrition tips for this fitness profile: {profile}. "
        "Return only valid JSON with string keys guidance, daily_habits (array of three "
        "strings), and meal_ideas (object with breakfast, lunch, snack, dinner strings). "
        "Avoid medical claims.",
    )
    generated = _extract_json(raw_response)
    if (
        not isinstance(generated, dict)
        or not isinstance(generated.get("guidance"), str)
        or not isinstance(generated.get("daily_habits"), list)
        or not generated["daily_habits"]
        or not isinstance(generated.get("meal_ideas"), dict)
        or not generated["meal_ideas"]
    ):
        raise ValueError("Gemini returned invalid nutrition data")
    return generated
