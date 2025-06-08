from fastapi import FastAPI
from smart_buddy.routers import index

app = FastAPI()

app.include_router(index.router)

@app.get("/")
def read_root():
    return {"message": "SMART BUDDY environment setup successful!"}
