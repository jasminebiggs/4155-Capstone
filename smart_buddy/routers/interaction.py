from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.sqlalchemy_models import Profile, Session as StudySession
from starlette.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="smart_buddy/templates")

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Profile).filter_by(username=username, password=password).first()
    if user:
        request.session["username"] = username
        print(f"✅ Logged in as: {username}")
        return RedirectResponse(url="/home", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@router.get("/home", response_class=HTMLResponse)
def get_home(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    return templates.TemplateResponse("home.html", {"request": request, "username": username})

@router.get("/matched-users", response_class=HTMLResponse)
def get_matched_users(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    matched_users = []

    if username == "jbiggs7":
        mock_user = db.query(Profile).filter(Profile.username == "biggsjasmine05").first()
        if mock_user:
            matched_users = [mock_user]

    return templates.TemplateResponse("matched_users.html", {
        "request": request,
        "matched_users": matched_users,
        "username": username
    })

@router.get("/schedule", response_class=HTMLResponse)
def view_schedule(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    scheduled_sessions = []

    if username == "jbiggs7":
        user = db.query(Profile).filter(Profile.username == username).first()
        if user:
            scheduled_sessions = db.query(StudySession).filter(
                (StudySession.student1_id == user.id) | (StudySession.student2_id == user.id)
            ).all()

    return templates.TemplateResponse("schedule.html", {
        "request": request,
        "sessions": scheduled_sessions,
        "username": username
    })

@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/ratings", response_class=HTMLResponse)
async def submit_rating(
    request: Request,
    session_id: int = Form(...),
    reviewer_id: int = Form(...),
    partner_id: int = Form(...),
    rating: int = Form(...),
    feedback: str = Form(...)
):
    # Save logic here or just show success
    return templates.TemplateResponse(
        "success.html",
        {"request": request, "username": request.session.get("username")}
    )