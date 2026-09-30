# 3. Project Design Phase

## System Architecture

User
   ↓
Web Interface
   ↓
FastAPI Backend
   ↓
Gemini AI
   ↓
Workout / Nutrition Response
   ↓
SQLite Database

## Modules

### 1. User Profile Module
Collects:
- Name
- Age
- Height
- Weight
- Goal

### 2. AI Workout Module
Generates personalized workout plans using Gemini AI.

### 3. Nutrition Module
Provides nutrition guidance and meal ideas.

### 4. Feedback Module
Allows users to submit ratings and comments.

### 5. Admin Module
Allows authorized admin users to view profiles and feedback.

## Database

The project uses SQLite to store:
- User profiles
- Fitness plans
- Feedback
