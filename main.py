from fastapi import FastAPI

from router import publications 

app = FastAPI()

app.include_router(publications.router)