# main.py
# completed on June 22

from fastapi import FastAPI
from routes.ratings import router
from database import database

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
