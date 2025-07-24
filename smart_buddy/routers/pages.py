import json
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.models.sqlalchemy_models import Profile
from fastapi.templating import Jinja2Templates
from smart_buddy.db import SessionLocal
from pydantic import BaseModel


router = APIRouter()
templates = Jinja2Templates(directory="smart_buddy/templates")

class AvailabilityUpdate(BaseModel):
    user_id: int
    availability: dict

@router.get("/", response_class=HTMLResponse)
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
def read_schedule(request: Request, user_id: int = None, db: Session = Depends(get_db)):
    try:
        # Get all profiles for the dropdown
        all_profiles = db.query(Profile).all()
        
        # Determine which user to display
        user_to_display = None
        if user_id:
            user_to_display = db.query(Profile).filter(Profile.id == user_id).first()
        elif all_profiles:
            # If no user_id is specified, default to the first user
            user_to_display = all_profiles[0]

        current_user_id = None
        availability = {}
        
        if user_to_display:
            current_user_id = user_to_display.id
            # Ensure availability is a dict, not a string
            if isinstance(user_to_display.availability, str):
                try:
                    availability = json.loads(user_to_display.availability)
                except json.JSONDecodeError:
                    availability = {} # or handle error appropriately
            else:
                availability = user_to_display.availability if user_to_display.availability else {}
        
        return templates.TemplateResponse("schedule.html", {
            "request": request, 
            "all_profiles": all_profiles,
            "current_user_id": current_user_id,
            "availability": availability
        })
    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred in /schedule: {e}")
        # Return a user-friendly error page
        return HTMLResponse(content="<h1>Error</h1><p>Could not load schedule data. The database might be empty or unavailable.</p>", status_code=500)

@router.get("/matched-users", response_class=HTMLResponse)
def read_matched_users(request: Request):
    return templates.TemplateResponse("matched_users.html", {"request": request})

@router.get("/ratings", response_class=HTMLResponse)
def read_ratings(request: Request):
    return templates.TemplateResponse("ratings.html", {"request": request})

@router.get("/availability", response_class=HTMLResponse)
def read_availability(request: Request):
    return templates.TemplateResponse("availability.html", {"request": request})

@router.get("/matches", response_class=HTMLResponse)
async def matches_page(request: Request, db: Session = Depends(get_db)):
    """Display the study buddy matching page"""
    # Get all profiles for the dropdown
    profiles = db.query(Profile).all()
    
    return templates.TemplateResponse("matches.html", {
        "request": request,
        "profiles": profiles,
        "current_student_id": None,
        "matches": None,
        "scheduling_analysis": None
    })

@router.post("/availability")
async def update_availability(update: AvailabilityUpdate, db: Session = Depends(get_db)):
    """Update a user's availability schedule (for demo purposes, no auth required)"""
    try:
        # Find the user
        user = db.query(Profile).filter(Profile.id == update.user_id).first()
        if not user:
            return JSONResponse(
                status_code=404,
                content={"detail": f"User with ID {update.user_id} not found"}
            )
        
        # Validate availability data
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        valid_times = ["Morning", "Afternoon", "Evening"]
        
        for day, times in update.availability.items():
            if day not in valid_days:
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"Invalid day: {day}. Must be one of {valid_days}"}
                )
            if not isinstance(times, list):
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"Times for {day} must be a list"}
                )
            for time_slot in times:
                if time_slot not in valid_times:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": f"Invalid time slot: {time_slot}. Must be one of {valid_times}"}
                    )
        
        # Update the user's availability
        user.availability = json.dumps(update.availability)
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Availability updated successfully for {user.username}",
                "user_id": user.id,
                "username": user.username,
                "availability": user.availability
            }
        )
        
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error updating availability: {str(e)}"}
        )

