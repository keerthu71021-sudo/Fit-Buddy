from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    id: int
    name: str
    age: int
    height_cm: float
    weight_kg: float
    goal: str


@dataclass(frozen=True)
class Feedback:
    id: int
    profile_id: int | None
    rating: int
    message: str
