from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

# Fix imports to use the correct module path
from .sqlalchemy_models import Base
from .db import engine, get_db

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Buddy API")

app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")
app.mount('/static', StaticFiles(directory='smart_buddy/static'), name='static')
templates = Jinja2Templates(directory="smart_buddy/templates")

# Add a root endpoint to redirect to home
@app.get("/")
def redirect_to_home():
    return RedirectResponse(url="/home", status_code=303)

# --- LOGIN & PROFILE CREATION ---

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # For demo, any username/password is accepted
    request.session["username"] = username
    return RedirectResponse(url="/home", status_code=303)

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request):
    username = request.session.get("username")
    return templates.TemplateResponse("profile.html", {"request": request, "username": username})

@app.post("/profile", response_class=HTMLResponse)
async def post_profile(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    study_style: str = Form(...),
    preferred_environment: str = Form(...),
    personality_traits: str = Form(...),
    academic_focus_areas: str = Form(...),
    password: str = Form(...),
    availability: str = Form(...)
):
    # In a real app, save to DB. For demo, just set session.
    request.session["username"] = username
    return templates.TemplateResponse("success.html", {"request": request, "username": username})

# --- HOME ---

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    username = request.session.get("username")
    return templates.TemplateResponse("home.html", {"request": request, "username": username})

# --- NOT AUTHORIZED PAGE ---
@app.get("/not-authorized", response_class=HTMLResponse)
async def not_authorized(request: Request):
    username = request.session.get("username")
    return templates.TemplateResponse("not_authorized.html", {"request": request, "username": username})


@app.get("/matched-users", response_class=HTMLResponse)
async def matched_users(request: Request):
    username = request.session.get("username")
    if not username:
        return RedirectResponse("/login", status_code=303)
    matched_profiles = [
        {
            "username": "biggsjasmine05",
            "study_style": "Visual",
            "environment": "Library",
            "profile_pic": "662972b3-bddd-4c76-9ad9-d2faa98670f2.png",
            "matched_on": "Calculus II",
            "next_session": "Monday, 2:00 PM"
        },
        {
            "username": "johnstudent1",
            "study_style": "Auditory",
            "environment": "Cafe",
            "profile_pic": "04d418f1-b15a-456b-ac89-00c79661fc91.png",
            "matched_on": "Cybersecurity",
            "next_session": "Wednesday, 11:00 AM"
        },
    ]
    return templates.TemplateResponse(
        "matched_users.html",
        {"request": request, "username": username, "matched_profiles": matched_profiles}
    )

@app.get("/schedule", response_class=HTMLResponse)
async def schedule(request: Request):
    username = request.session.get("username")
    if not username:
        return RedirectResponse("/login", status_code=303)
    sessions = [
        {"day": "Monday", "time": "2:00 PM", "subject": "Calculus II"},
        {"day": "Wednesday", "time": "11:00 AM", "subject": "Cybersecurity"},
        {"day": "Friday", "time": "9:30 AM", "subject": "Data Structures"},
    ]
    return templates.TemplateResponse(
        "schedule.html",
        {"request": request, "username": username, "sessions": sessions}
    )


# --- RATINGS (PROTECTED) ---

@app.get("/ratings", response_class=HTMLResponse)
async def ratings(request: Request):
    username = request.session.get("username")
    if not username:
        return RedirectResponse("/login", status_code=303)
    if username != "jbiggs7":
        return RedirectResponse("/not-authorized", status_code=303)
    ratings = [
        {"session": "Calculus II", "partner": "biggsjasmine05", "score": 5, "feedback": "Great session!"},
        {"session": "Cybersecurity", "partner": "johnstudent1", "score": 4, "feedback": "Very helpful."},
    ]
    return templates.TemplateResponse(
        "ratings.html",
        {
            "request": request,
            "username": username,
            "ratings": ratings
        }
    )

@app.post("/ratings", response_class=HTMLResponse)
async def submit_rating(
    request: Request,
    session_id: int = Form(...),
    reviewer_id: int = Form(...),
    partner_id: int = Form(...),
    rating: int = Form(...),
    feedback: str = Form(...)
):
    # Save to DB logic goes here if needed
    return templates.TemplateResponse(
        "rating_success.html",  # <- new template!
        {"request": request, "username": request.session.get("username")}
    )

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
