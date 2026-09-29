import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WORKOUT_MODEL = os.getenv("FITBUDDY_WORKOUT_MODEL", "gemini-2.5-pro")
TIP_MODEL = os.getenv("FITBUDDY_TIP_MODEL", "gemini-2.5-flash")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
APP_ENV = os.getenv("APP_ENV", "development")
