from pydantic import BaseModel

class UserProfileCreate(BaseModel):
    name: str
    email: str
    personality_type: str
    study_style: str
    environment: str
    focus_area: str
