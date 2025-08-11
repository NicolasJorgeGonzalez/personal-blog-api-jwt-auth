from fastapi import APIRouter, HTTPException, status, Form, Depends
from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId

from db.client import db
from db.models.publication import Publication
from db.models.user import User
from db.schemas.publication import publicationSchema
from utils.publicationsUtils import srcPublicationId
from utils.authUtils import verifyTokenAccess

router = APIRouter(
    prefix="/pb",
    tags=["publications"]
)

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def createPb(title:str = Form(...), content:str = Form(...), category:str = Form(...), tags:List[str] = Form(...), auth:User = Depends(verifyTokenAccess)):
    try:
        pb = {
            "userId": auth.id,
            "title":title,
            "content":content,
            "category":category,
            "tags":tags,
            "createdAt": datetime.now(timezone.utc).isoformat(timespec='seconds'),
            "updatedAt": datetime.now(timezone.utc).isoformat(timespec='seconds')
        }
        
        insertedPb = db.publications.insert_one(pb).inserted_id
        return Publication(**srcPublicationId(insertedPb))
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot create de publication"})

@router.get("/get/{id}", status_code=status.HTTP_200_OK)
async def getPb(id:str, auth:User = Depends(verifyTokenAccess)):
    try:
        publicationDb = srcPublicationId(ObjectId(id))
        if publicationDb["userId"] == auth.id:
            return Publication(**publicationDb)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this publication")
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot get de publication"})

@router.get("/all", status_code=status.HTTP_200_OK)
async def getAllPb(auth:User = Depends(verifyTokenAccess)):
    try:
        if auth.is_superuser:
            pbList:List[Publication] = []
            publications = db.publications.find()
        for publication in publications:
            publication["_id"] = str(publication["_id"])
            pbList.append(publication)
        return pbList
    except HTTPException as exception:
        raise exception

@router.get("/term/{term}")
async def getTermPb(term:str, auth:User = Depends(verifyTokenAccess)):
    try:
        pbList:List[Publication] = []
        publications = db.publications.find(
            {
            "$and": [
                {"userId": auth.id},
                {
                "$or": [
                    {"title": {"$regex": term, "$options": "i"}},
                    {"content": {"$regex": term, "$options": "i"}},
                    {"category": {"$regex": term, "$options": "i"}}
                ]
                }
            ]
            }
        )
        for publication in publications:
            publication["_id"] = str(publication["_id"])
            pbList.append(publication)
        return pbList
    except HTTPException as exception:
        raise exception

@router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def updatePb(id:str, title:str  = Form(None), content:str  = Form(None), category:str  = Form(None), tags:Optional[List[str]]  = Form(None), auth:User = Depends(verifyTokenAccess)):
    try:
        publicationDb = srcPublicationId(ObjectId(id))
        if publicationDb["userId"] == auth.id:
            updatedPb = db.publications.find_one_and_replace(
                {"_id":ObjectId(id)},
                {
                    "title": title if title is not None else publicationDb["title"],
                    "content": content if content is not None else publicationDb["content"],
                    "category": category if category is not None else publicationDb["category"],
                    "tags": tags if tags is not None else publicationDb["tags"],
                    "createdAt":publicationDb["createdAt"],
                    "updatedAt": datetime.now(timezone.utc).isoformat(timespec='seconds')
                },
                return_document=True
            )
            
            return Publication(**publicationSchema(updatedPb))
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this publication")
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot update de publication"})

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePb(id:str, auth:User = Depends(verifyTokenAccess)):
    try:
        publicationDb = db.publications.find_one({"_id":ObjectId(id)})
        if publicationDb["userId"] == auth.id:
            db.publications.delete_one({"_id":ObjectId(id)})
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this publication")
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot delete de publication"})
