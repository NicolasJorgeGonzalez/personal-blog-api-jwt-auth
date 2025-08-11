from fastapi import HTTPException, status
from bson import ObjectId

from db.client import db
from db.schemas.user import userSchema

def srcUserName(username:str):
    try:
        user = db.users.find_one({"username":username})
        return userSchema(user)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
def srcUserID(id:ObjectId):
    try:
        user = db.users.find_one({"_id":id})
        return userSchema(user)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")