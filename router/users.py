from fastapi import APIRouter, HTTPException, status, Depends, Form
from typing import List

from db.client import db
from db.models.user import User
from utils.authUtils import verifyTokenAccess, hashPassword
from utils.userUtils import *

router = APIRouter(
    prefix="/user",
    tags=["user"],  
)

@router.post("/create")
async def createUser(username:str = Form(...), email:str = Form(...), password:str = Form(...)):
    try:
        srcUserName(username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username is already exist")
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            user = {
                "username":username,
                "email":email,
                "password":hashPassword(password)
            }
            insertedUser = db.users.insert_one(user).inserted_id
            return User(**srcUserID(insertedUser))
        else:
            raise exception

@router.get("/get/one/{id}")
async def getUser(id:str, auth:User = Depends(verifyTokenAccess)):
    try:
        if id == auth.id:
            return User(**srcUserID(ObjectId(id)))
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user")
    except HTTPException as exception:
        raise exception
    
@router.get("/get/all")
async def getAllUsers(auth:User = Depends(verifyTokenAccess)):
    try:
        if auth.is_superuser:
            usersList:List[User] = []
            users = db.users.find()
        for user in users:
            usersList.append(User(**userSchema(user)))
        return usersList
    except HTTPException as exception:
        raise exception

@router.put("/update/{id}")
async def updateUser(id:str, username:str = Form(None), email:str = Form(None), password:str = Form(None), auth:User = Depends(verifyTokenAccess)):
    try:
        user = srcUserID(ObjectId(id))
        if user["id"] == auth.id:
            updatedUser = db.users.find_one_and_replace(
                {"_id":ObjectId(id)},
                {
                    "username":username if username is not None else user["username"],
                    "email":email if email is not None else user["email"],
                    "password":password if password is not None else user["password"],
                },
                return_document=True
            )
            return User(**userSchema(updatedUser))
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    except HTTPException as exception:
        raise exception
    
@router.delete("/delete/{id}")
async def deleteUser(id:str, auth:User = Depends(verifyTokenAccess)):
    try:
        user = srcUserID(ObjectId(id))
        if user["id"] == auth.id:
            db.users.delete_one({"_id":ObjectId(id)})
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
    except HTTPException as exception:
        raise exception
