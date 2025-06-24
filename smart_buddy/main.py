from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from smart_buddy.routers import index, user_profile as user_profile_router
from smart_buddy.models import user_profile as user_profile_model
from smart_buddy import db
import smart_buddy.logic as logic
from smart_buddy.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount routers
app.include_router(index.router)
app.include_router(user_profile_router.router)

# Static files and templates
app.mount("/static", StaticFiles(directory="smart_buddy/static"), name="static")
templates = Jinja2Templates(directory="smart_buddy/templates")

# Routes
@app.get("/")
def read_root():
    return {"message": "SMART BUDDY environment setup successful!"}

@app.get("/match/{name}")
def match_user(name: str):
    result = logic.get_study_partner(name)
    return {"result": result}

@app.get("/dbtest")
def test_mysql():
    msg = db.test_connection()
    return {"message": msg}

@app.get("/create-profile", response_class=HTMLResponse)
async def show_create_profile(request: Request):
    return templates.TemplateResponse("create_profile.html", {"request": request, "profile": {}})

