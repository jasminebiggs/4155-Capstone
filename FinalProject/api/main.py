import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import index as indexRoute
from .routers import resources as resourcesRoute
from .routers import promotions as promotionsRoute
from .models import model_loader
from .dependencies.config import conf
from .routers import sandwiches as sandwichesRoute



app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_loader.index()
indexRoute.load_routes(app)

app.include_router(resourcesRoute.router)

app.include_router(promotionsRoute.router)

app.include_router(sandwichesRoute.router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
if __name__ == "__main__":
    uvicorn.run(app, host=conf.app_host, port=conf.app_port)