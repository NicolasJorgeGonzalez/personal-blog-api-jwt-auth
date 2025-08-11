from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from db.models.user import User
from utils.userUtils import srcUserName
from env.auth import ALGORITHM, SECRET_KEY, TOKEN_EXPIRATION

pwd = CryptContext(schemes=["bcrypt"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def hashPassword(password:str):
    return pwd.hash(password)

def verifyPassword(password:str, userPassword:str):
    if not (pwd.verify(password, userPassword)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    else:
        return True

def createTokenAccess(user):
    try:
        json = {
            "username": user["username"],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION)
        }
        return jwt.encode(json, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as exception:
        raise exception
        
def verifyTokenAccess(token:str = Depends(oauth2)):
    try:
        json = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_exp":True})
        user = srcUserName(json["username"])
        return User(**user)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
  