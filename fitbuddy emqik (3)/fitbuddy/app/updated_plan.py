from .ai_common import generate_gemini_text
from .config import WORKOUT_MODEL


def update_workout_plan(profile: dict, current_plan: str, rating: int, feedback: str) -> str:
    return generate_gemini_text(
        WORKOUT_MODEL,
        "Revise this seven-day fitness plan using the user's feedback. Keep Monday through "
        "Sunday labels, preserve at least two recovery days, and remain beginner-friendly. "
        f"Avoid medical claims.\n\nProfile: {profile}\nCurrent plan:\n{current_plan}\n\n"
        f"Feedback ({rating}/5): {feedback}",
    )
