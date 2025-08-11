from fastapi import HTTPException, status
from bson import ObjectId

from db.client import db
from db.schemas.publication import publicationSchema


def srcPublicationId(id:ObjectId):
    try:
        publicationDb = db.publications.find_one({"_id":id})
        return publicationSchema(publicationDb)
    except:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Publication not found")