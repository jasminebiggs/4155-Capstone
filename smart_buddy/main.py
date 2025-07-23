
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from . import db
from .routers import index, pages, interaction
from smart_buddy.routers import rating, availability


app = FastAPI()
app.mount('/static', StaticFiles(directory='smart_buddy/static'), name='static')

templates = Jinja2Templates(directory="smart_buddy/templates")

app.include_router(rating.router) 
app.include_router(availability.router)
app.include_router(index.router)
app.include_router(pages.router)
app.include_router(interaction.router)

@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request):
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
    from .db import SessionLocal
    from .models.sqlalchemy_models import Profile
    from sqlalchemy.exc import IntegrityError
    
    # Get form data and process availability
    form_data = await request.form()
    availability = {}
    
    # Process availability checkboxes
    for key, value in form_data.items():
        if key.startswith('availability[') and key.endswith('][]'):
            # Extract day from key like 'availability[Monday][]'
            day = key.split('[')[1].split(']')[0]
            if day not in availability:
                availability[day] = []
            if isinstance(value, list):
                availability[day].extend(value)
            else:
                availability[day].append(value)

    db_session = SessionLocal()
    try:
        # Check if username or email already exists
        existing_username = db_session.query(Profile).filter(Profile.username == username).first()
        if existing_username:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "error_message": f"Username '{username}' is already taken. Please choose a different username."
            })
        
        existing_email = db_session.query(Profile).filter(Profile.email == email).first()
        if existing_email:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "error_message": f"Email '{email}' is already registered. Please use a different email address."
            })
        
        profile = Profile(
            email=email,
            username=username,
            password=password,
            personality_traits=personality_traits,
            study_style=study_style,
            preferred_environment=preferred_environment,
            academic_focus_areas=academic_focus_areas,
            availability=availability
        )
        db_session.add(profile)
        db_session.commit()
        return templates.TemplateResponse("profile.html", {"request": request, "success_message": "Profile created successfully!"})
    except IntegrityError as e:
        db_session.rollback()
        if "UNIQUE constraint failed: profiles.username" in str(e):
            error_msg = f"Username '{username}' is already taken. Please choose a different username."
        elif "UNIQUE constraint failed: profiles.email" in str(e):
            error_msg = f"Email '{email}' is already registered. Please use a different email address."
        else:
            error_msg = "A profile with this information already exists. Please check your username and email."
        return templates.TemplateResponse("profile.html", {"request": request, "error_message": error_msg})
    except Exception as e:
        db_session.rollback()
        return templates.TemplateResponse("profile.html", {"request": request, "error_message": f"Error creating profile: {str(e)}"})
    finally:
        db_session.close()
