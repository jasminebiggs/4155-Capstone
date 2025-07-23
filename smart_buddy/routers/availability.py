from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.models.sqlalchemy_models import Profile
from smart_buddy import schemas
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from smart_buddy.config import SECRET_KEY, ALGORITHM

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Profile).filter(Profile.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/availability", status_code=status.HTTP_200_OK)
def update_availability(
    availability: schemas.Availability,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user),
):
    user = db.query(Profile).filter(Profile.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Basic validation
    for day, times in availability.availability.items():
        if day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            raise HTTPException(status_code=400, detail=f"Invalid day: {day}")
        if not isinstance(times, list):
            raise HTTPException(status_code=400, detail=f"Times for {day} should be a list.")

    user.availability = availability.availability
    db.commit()
    return {"message": "Availability updated successfully"}

@router.get("/availability", response_model=schemas.Availability)
def get_availability(
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user),
):
    user = db.query(Profile).filter(Profile.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"availability": user.availability or {}}
