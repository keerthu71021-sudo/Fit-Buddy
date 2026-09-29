import json
import secrets

from fastapi import APIRouter, Header, HTTPException

from . import config
from .database import (
    create_profile,
    get_latest_fitness_plan,
    get_profile,
    get_profiles_with_feedback,
    save_feedback,
    save_fitness_plan,
)
from .gemini_flash_generator import generate_nutrition
from .gemini_generator import generate_workout_plan as generate_gemini_workout_plan
from .schemas import FeedbackCreate, ProfileCreate
from .updated_plan import update_workout_plan

router = APIRouter()


def fallback_nutrition() -> dict:
    return {
        "guidance": "Use these as general ideas, not medical advice.",
        "daily_habits": [
            "Include a protein source and colorful produce at each main meal.",
            "Choose water regularly and adjust intake for your activity level.",
            "Build meals around minimally processed foods most of the time.",
        ],
        "meal_ideas": {
            "breakfast": "Greek yogurt, oats, berries, and nuts",
            "lunch": "Grilled chicken or tofu grain bowl with vegetables",
            "snack": "Fruit with yogurt or a handful of nuts",
            "dinner": "Salmon, beans, or lean protein with vegetables and rice",
        },
    }


def fallback_workout_plan() -> str:
    return (
        "7-DAY STARTER PLAN\n\n"
        "Monday: Full-body strength - 3 sets of squats, incline push-ups, and glute bridges.\n"
        "Tuesday: Light cardio - 25-minute brisk walk and gentle stretching.\n"
        "Wednesday: Upper body and core - 3 sets of rows, shoulder presses, and planks.\n"
        "Thursday: Recovery - Rest or take an easy 20-minute walk.\n"
        "Friday: Lower body strength - 3 sets of lunges, hip hinges, and calf raises.\n"
        "Saturday: Cardio and mobility - 30-minute moderate cardio followed by stretching.\n"
        "Sunday: Recovery - Rest, hydrate, and prepare for the next week.\n\n"
        "Increase intensity gradually and stop if you feel pain."
    )


@router.post("/profiles", status_code=201)
def create_user_profile(profile: ProfileCreate):
    return create_profile(**profile.model_dump())


@router.get("/profiles/{profile_id}")
def read_user_profile(profile_id: int):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/feedback", status_code=201)
def create_feedback(feedback: FeedbackCreate):
    feedback_id = save_feedback(**feedback.model_dump())
    updated_plan = None
    if feedback.profile_id and config.GEMINI_API_KEY:
        profile = get_profile(feedback.profile_id)
        previous_plan = get_latest_fitness_plan(profile["id"]) if profile else None
        if profile and previous_plan:
            try:
                updated_plan = update_workout_plan(
                    profile, previous_plan, feedback.rating, feedback.message
                )
                save_fitness_plan(profile["id"], profile["name"], updated_plan)
            except Exception:
                updated_plan = None
    return {
        "feedback_id": feedback_id,
        "message": "Thank you for your feedback.",
        "updated_plan": updated_plan,
    }


@router.get("/admin/users")
def read_admin_users(x_admin_token: str | None = Header(default=None)):
    admin_token = config.ADMIN_TOKEN
    if not admin_token or not x_admin_token or not secrets.compare_digest(
        x_admin_token.encode(), admin_token.encode()
    ):
        raise HTTPException(status_code=401, detail="Valid admin token required")
    return {"users": get_profiles_with_feedback()}


@router.post("/profiles/{profile_id}/workout-plan")
def generate_workout_plan(profile_id: int):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    goal = profile["goal"].lower()
    if "strength" in goal or "muscle" in goal:
        exercises = [
            {"name": "Bodyweight squats", "sets": 3, "reps": 12},
            {"name": "Push-ups", "sets": 3, "reps": 10},
            {"name": "Glute bridges", "sets": 3, "reps": 12},
            {"name": "Plank", "sets": 3, "seconds": 30},
        ]
    elif "weight" in goal or "fat" in goal:
        exercises = [
            {"name": "Brisk walk", "minutes": 20},
            {"name": "Bodyweight squats", "sets": 3, "reps": 12},
            {"name": "Step-ups", "sets": 3, "reps": 10},
            {"name": "Mountain climbers", "sets": 3, "reps": 20},
        ]
    else:
        exercises = [
            {"name": "Brisk walk", "minutes": 20},
            {"name": "Bodyweight squats", "sets": 2, "reps": 10},
            {"name": "Incline push-ups", "sets": 2, "reps": 8},
            {"name": "Plank", "sets": 2, "seconds": 20},
        ]

    plan = {
        "profile_id": profile_id,
        "goal": profile["goal"],
        "frequency": "3 days per week",
        "exercises": exercises,
    }
    plan_id = save_fitness_plan(profile_id, profile["name"], json.dumps(plan))
    return {"plan_id": plan_id, **plan}


@router.get("/profiles/{profile_id}/nutrition")
def get_nutrition_recommendations(profile_id: int):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    nutrition = fallback_nutrition()
    if config.GEMINI_API_KEY:
        try:
            nutrition = generate_nutrition(profile)
        except Exception:
            pass

    return {"profile_id": profile_id, **nutrition, "goal": profile["goal"]}


@router.post("/profiles/{profile_id}/ai-plan")
def generate_ai_plan(profile_id: int):
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    if not config.GEMINI_API_KEY:
        plan = fallback_workout_plan()
        save_fitness_plan(profile_id, profile["name"], plan)
        return {
            "profile_id": profile_id,
            "source": "local-fallback",
            "message": "Add GEMINI_API_KEY to .env to enable AI-generated plans.",
            "plan": plan,
        }

    try:
        plan = generate_gemini_workout_plan(profile)
        save_fitness_plan(profile_id, profile["name"], plan)
        return {
            "profile_id": profile_id,
            "source": "gemini",
            "model": config.WORKOUT_MODEL,
            "plan": plan,
        }
    except Exception:
        plan = fallback_workout_plan()
        save_fitness_plan(profile_id, profile["name"], plan)
        return {
            "profile_id": profile_id,
            "source": "local-fallback",
            "message": "The AI service was unavailable, so a starter plan was returned.",
            "plan": plan,
        }
