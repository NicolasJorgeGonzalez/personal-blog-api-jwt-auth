from fastapi import HTTPException, status

def userSchema(user):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        return {
            "id":str(user["_id"]),
            "username":user["username"],
            "email":user["email"],
            "password":user["password"]
        }