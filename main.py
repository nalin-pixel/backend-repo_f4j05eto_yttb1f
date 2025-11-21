import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Miniapp, Transferlog

app = FastAPI(title="ViralCoin Mini Apps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "ViralCoin API running"}


# Mini App Store endpoints
class MiniAppCreate(BaseModel):
    name: str
    description: str
    url: str
    icon: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = []


@app.post("/api/miniapps")
def create_miniapp(payload: MiniAppCreate):
    try:
        miniapp = Miniapp(**payload.model_dump())
        inserted_id = create_document("miniapp", miniapp)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/miniapps")
def list_miniapps():
    try:
        items = get_documents("miniapp", {}, limit=100)
        # Convert ObjectId to str
        for item in items:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
        return {"ok": True, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Transfer logging endpoint (note: signing happens client-side; backend only logs metadata)
class TransferLogCreate(BaseModel):
    from_pubkey: str
    to_pubkey: str
    amount_sol: float
    signature: Optional[str] = None
    network: str = "mainnet-beta"
    note: Optional[str] = None


@app.post("/api/transfers/log")
def log_transfer(payload: TransferLogCreate):
    try:
        doc = Transferlog(**payload.model_dump())
        inserted_id = create_document("transferlog", doc)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/transfers")
def list_transfers(limit: int = 50):
    try:
        items = get_documents("transferlog", {}, limit=limit)
        for item in items:
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
        return {"ok": True, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
