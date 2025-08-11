from fastapi import APIRouter, HTTPException, status, Form
from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId

from db.client import db
from db.models.publication import Publication
from db.schemas.publication import publication_schema
from utils.publicationsUtils import srcId

router = APIRouter(
    prefix="/pb",
    tags=["publications"]
)

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def createPb(title:str = Form(...), content:str = Form(...), category:str = Form(...), tags:List[str] = Form(...)):
    try:
        pb = {
            "title":title,
            "content":content,
            "category":category,
            "tags":tags,
            "createdAt": datetime.now(timezone.utc).isoformat(timespec='seconds'),
            "updatedAt": datetime.now(timezone.utc).isoformat(timespec='seconds')
        }
        
        insertedPb = db.publications.insert_one(pb).inserted_id
        return Publication(**srcId(insertedPb))
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot create de publication"})

@router.get("/get/{id}", status_code=status.HTTP_200_OK)
async def getPb(id:str):
    try:
        publicationDb = srcId(ObjectId(id))
        return Publication(**publicationDb)
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot get de publication"})

@router.get("/all", status_code=status.HTTP_200_OK)
async def getAllPb():
    try:
        pbList = List[Publication]
        pbList = []
        publications = db.publications.find()
        for publication in publications:
            publication["_id"] = str(publication["_id"])
            pbList.append(publication)
        return pbList
    except HTTPException as exception:
        raise exception

@router.get("/term/{term}")
async def getTermPb(term:str):
    try:
        pbList = List[Publication]
        pbList = []
        publications = db.publications.find(
            {
                "$or":[
                    {"title":{"$regex":term, "$options":"i"}},
                    {"content":{"$regex":term, "$options":"i"}},
                    {"category":{"$regex":term, "$options":"i"}}
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
async def updatePb(id:str, title:str  = Form(None), content:str  = Form(None), category:str  = Form(None), tags:Optional[List[str]]  = Form(None)):
    try:
        publicationDb = srcId(ObjectId(id))
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
        
        return Publication(**publication_schema(updatedPb))
    
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot update de publication"})

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePb(id:str):
    try:
        db.publications.delete_one({"_id":ObjectId(id)})
    except HTTPException as exception:
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"error: cannot delete de publication"})
