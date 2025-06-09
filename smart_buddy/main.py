from fastapi import FastAPI
from smart_buddy.routers import index
from smart_buddy import db

app = FastAPI()

app.include_router(index.router)

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