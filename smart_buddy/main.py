from smart_buddy.routers import index
from smart_buddy import db
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from smart_buddy.routers import user_profile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(index.router)
app.include_router(user_profile.router)

app.mount("/static", StaticFiles(directory="smart_buddy/static"), name="static")

templates = Jinja2Templates(directory="smart_buddy/templates")
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

def get_user_name():
    return "Adam Pang"

@app.get("/create-profile", response_class=HTMLResponse)
async def show_create_profile(request: Request):
    return templates.TemplateResponse("create_profile.html", {"request": request, "profile": {}})

