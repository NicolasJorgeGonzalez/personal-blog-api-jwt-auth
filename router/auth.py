from fastapi import APIRouter, HTTPException, status, Depends, Form

from utils.authUtils import *
from utils.userUtils import srcUserName

router = APIRouter()

@router.post("/login")
async def login(username:str = Form(...), password:str = Form(...)):
    try:
        user = srcUserName(username)
        if verifyPassword(password, user["password"]):
            token = createTokenAccess(user)
            return {"token":token, "token_type":"bearer"}
    except HTTPException as exception:
        raise exception