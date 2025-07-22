from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.models.sqlalchemy_models import Profile
from fastapi.templating import Jinja2Templates
from smart_buddy.db import SessionLocal


router = APIRouter()
templates = Jinja2Templates(directory="smart_buddy/templates")

@router.get("/home", response_class=HTMLResponse)
def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)
def read_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@router.post("/profile")
async def create_profile(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    study_style: str = Form(...),
    preferred_environment: str = Form(...),
    personality_traits: str = Form(...),
    academic_focus_areas: str = Form(...),
    password: str = Form(...),
    availability: list[str] = Form(default=[])
):
    db = SessionLocal()
    try:
        profile = Profile(
            email=email,
            username=username,
            study_style=study_style,
            preferred_environment=preferred_environment,
            personality_traits=personality_traits,
            academic_focus_areas=academic_focus_areas,
            password=password,
            availability=availability  # Must be declared as JSON in model
        )
        db.add(profile)
        db.commit()
        return templates.TemplateResponse("success.html", {"request": request, "username": username})
    except Exception as e:
        db.rollback()
        print(e)
        return HTMLResponse(content="An error occurred: " + str(e), status_code=500)
    finally:
        db.close()
@router.get("/schedule", response_class=HTMLResponse)
def read_schedule(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})

@router.get("/matched-users", response_class=HTMLResponse)
def read_matched_users(request: Request):
    return templates.TemplateResponse("matched_users.html", {"request": request})

@router.get("/ratings", response_class=HTMLResponse)
def read_ratings(request: Request):
    return templates.TemplateResponse("ratings.html", {"request": request})

