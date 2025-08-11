from fastapi import HTTPException, status
from datetime import date

def publication_schema(publication): # -> publication viene de la base de datos
    if not publication:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Publication eq None")
    else:
        return {
            "id":str(publication["_id"]),
            "title":publication["title"],
            "content":publication["content"],
            "category":publication["category"],
            "tags":publication["tags"],
            "createdAt":publication["createdAt"],
            "updatedAt":publication["updatedAt"]
        }
