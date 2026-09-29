from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=120)
    height_cm: float = Field(gt=0, le=300)
    weight_kg: float = Field(gt=0, le=500)
    goal: str = Field(min_length=1, max_length=200)


class FeedbackCreate(BaseModel):
    profile_id: int | None = Field(default=None, gt=0)
    rating: int = Field(ge=1, le=5)
    message: str = Field(min_length=1, max_length=1000)
