from fastapi import HTTPException, status
from bson import ObjectId

from db.client import db
from db.schemas.publication import publication_schema


def srcId(id:ObjectId):
    publicationDb = db.publications.find_one({"_id":id})
    if not publicationDb:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Publication not found")
    else:
        return publication_schema(publicationDb)
    