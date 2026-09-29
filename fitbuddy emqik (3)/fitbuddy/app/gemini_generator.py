from .ai_common import generate_gemini_text
from .config import WORKOUT_MODEL


def generate_workout_plan(profile: dict) -> str:
    return generate_gemini_text(
        WORKOUT_MODEL,
        f"Create a concise, beginner-friendly seven-day fitness plan for this profile: {profile}. "
        "Label every day from Monday through Sunday. Include workouts, at least two recovery "
        "days, and general nutrition guidance. Adapt the intensity to the user's experience. "
        "Avoid medical claims.",
    )
