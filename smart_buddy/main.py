
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from . import db
from .routers import index, pages, interaction
from smart_buddy.routers import rating


app = FastAPI()
app.mount('/static', StaticFiles(directory='smart_buddy/static'), name='static')

templates = Jinja2Templates(directory="smart_buddy/templates")

app.include_router(rating.router) 
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
    academic_focus: str = Form(...),
    password: str = Form(...)
):
    from .db import SessionLocal
    from .models.sqlalchemy_models import UserProfile

    db_session = SessionLocal()
    profile = UserProfile(
        email=email,
        password=password,
        personality_traits=personality_traits,
        study_style=study_style,
        preferred_environment=preferred_environment,
        academic_focus=academic_focus
    )
    db_session.add(profile)
    db_session.commit()
    db_session.close()
    return templates.TemplateResponse("profile.html", {"request": request, "success_message": "Profile created successfully!"})
