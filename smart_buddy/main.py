from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

# --- Local Imports & Database ---
# Combining imports from both branches to include all modules
from . import db
from .models.sqlalchemy_models import Profile
from .routers import index, pages, interaction, rating, availability, user_profile

# --- FastAPI App Initialization ---
app = FastAPI()

# Mount static files directory once
app.mount('/static', StaticFiles(directory='smart_buddy/static'), name='static')

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="smart_buddy/templates")

# --- Include Routers ---
# Including all routers from both branches to merge functionalities
app.include_router(index.router)
app.include_router(pages.router)
app.include_router(interaction.router)
app.include_router(rating.router)
app.include_router(availability.router)
app.include_router(user_profile.router) # From the 'main' branch

# --- Root Endpoint ---
# Kept from the 'main' branch as a simple welcome/health-check message
@app.get("/")
def read_root():
    return {"message": "SMART BUDDY environment setup successful!"}

# --- Profile Creation Endpoints ---
# Using the more complete implementation from the 'new-jasmine-sprint2' branch

@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request):
    """
    Handles GET requests to the profile page, rendering the profile form.
    """
    return templates.TemplateResponse("profile.html", {"request": request})

@app.post("/profile", response_class=HTMLResponse)
async def post_profile(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    study_style: str = Form(...),
    preferred_environment: str = Form(...),
    personality_traits: str = Form(...),
    academic_focus_areas: str = Form(...),
    password: str = Form(...)
):
    """
    Handles POST requests from the profile creation form.
    It validates the data, checks for existing users, and creates a new profile.
    """
    form_data = await request.form()
    availability_data = {}
    
    # Process availability checkboxes from the form
    for key, value in form_data.items():
        if key.startswith('availability[') and key.endswith('][]'):
            day = key.split('[')[1].split(']')[0]
            if day not in availability_data:
                availability_data[day] = []
            # Form data can send a single value or a list of values for checkboxes
            if isinstance(value, list):
                availability_data[day].extend(value)
            else:
                availability_data[day].append(value)

    db_session = db.SessionLocal()
    try:
        # Check if username already exists
        existing_username = db_session.query(Profile).filter(Profile.username == username).first()
        if existing_username:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "error_message": f"Username '{username}' is already taken. Please choose another."
            })
        
        # Check if email already exists
        existing_email = db_session.query(Profile).filter(Profile.email == email).first()
        if existing_email:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "error_message": f"Email '{email}' is already registered. Please use another."
            })
        
        # Create new profile object
        new_profile = Profile(
            email=email,
            username=username,
            password=password, # Note: In a real app, hash the password!
            personality_traits=personality_traits,
            study_style=study_style,
            preferred_environment=preferred_environment,
            academic_focus_areas=academic_focus_areas,
            availability=availability_data
        )
        db_session.add(new_profile)
        db_session.commit()
        
        return templates.TemplateResponse("profile.html", {"request": request, "success_message": "Profile created successfully!"})

    except IntegrityError:
        db_session.rollback()
        # This is a fallback for race conditions where the initial check passes but the commit fails
        return templates.TemplateResponse("profile.html", {
            "request": request, 
            "error_message": "A profile with this username or email already exists."
        })
    except Exception as e:
        db_session.rollback()
        return templates.TemplateResponse("profile.html", {
            "request": request, 
            "error_message": f"An unexpected error occurred: {str(e)}"
        })
    finally:
        db_session.close()
