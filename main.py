from fastapi import FastAPI

from router import publications, users, auth

app = FastAPI()

app.include_router(publications.router)
app.include_router(users.router)
app.include_router(auth.router)