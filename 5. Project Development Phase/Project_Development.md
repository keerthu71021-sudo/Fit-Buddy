# 5. Project Development Phase

## Frontend Development

The frontend is developed using:

- HTML
- CSS
- JavaScript

The frontend provides:
- User profile form
- Workout plan display
- Nutrition section
- Feedback form
- Admin section

## Backend Development

FastAPI is used to develop the backend.

The backend handles:
- User profiles
- AI workout generation
- Nutrition information
- Feedback
- Admin requests

## AI Integration

Google Gemini AI is integrated into the application.

The API key is stored using an environment variable:

GEMINI_API_KEY

## Database Development

SQLite is used as the database.

The database contains:

### profiles
Stores user information.

### fitness_plans
Stores generated fitness plans.

### feedback
Stores user ratings and comments.

## Main API Endpoints

POST /profiles
Creates a new user profile.

POST /profiles/{id}/ai-plan
Generates an AI workout plan.

GET /profiles/{id}/nutrition
Returns nutrition guidance.

POST /feedback
Stores user feedback.

GET /admin/users
Returns saved users for the admin.
