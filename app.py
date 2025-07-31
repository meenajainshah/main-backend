from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import httpx

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Main backend is running"}

MEMORY_AGENT_BASE_URL = "https://chromamemory.onrender.com/"  # Update this
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com//hooks/catch/12831161/2vjgzlr/"  # Update this

# Pydantic model for Zapier action payload
class ZapierPayload(BaseModel):
    user_input: str
    entity_id: str
    additional_info: Optional[Dict] = None

@app.post("/zapier-action")
async def zapier_action(payload: ZapierPayload):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(ZAPIER_WEBHOOK_URL, json=payload.dict())
            resp.raise_for_status()
            return {"status": "Zapier webhook triggered", "response": resp.json()}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error calling Zapier webhook: {str(e)}")

# Pydantic model for Memory store payload
class MemoryStorePayload(BaseModel):
    text: str
    metadata: Optional[Dict] = None

@app.post("/memory/store")
async def memory_store(payload: MemoryStorePayload):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{MEMORY_AGENT_BASE_URL}/store", json=payload.dict())
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error forwarding to memory agent store: {str(e)}")

# Pydantic model for Memory retrieve payload
class MemoryRetrievePayload(BaseModel):
    query: str
    entity_id: str
    platform: Optional[str] = None
    thread_id: Optional[str] = None
    top_k: Optional[int] = 5

@app.post("/memory/retrieve")
async def memory_retrieve(payload: MemoryRetrievePayload):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{MEMORY_AGENT_BASE_URL}/retrieve", json=payload.dict())
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error forwarding to memory agent retrieve: {str(e)}")
