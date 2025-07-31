from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import httpx
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update these URLs before deploying
MEMORY_AGENT_BASE_URL = "https://chromamemory.onrender.com"
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/12831161/u2j3pbl/"

# Models

class ZapierPayload(BaseModel):
    user_input: str
    entity_id: str
    task_type: str
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    scope: Optional[str] = None
    skills: Optional[str] = None
    tools: Optional[str] = None
    suggestedroadmap: Optional[str] = None
    budget: Optional[str] = None

class MemoryStorePayload(BaseModel):
    text: str
    metadata: Optional[Dict] = None

class MemoryRetrievePayload(BaseModel):
    query: str
    entity_id: str
    platform: Optional[str] = None
    thread_id: Optional[str] = None
    top_k: Optional[int] = 5

# Routes

@app.get("/")
async def root():
    return {"message": "Main backend is running"}

@app.post("/zapier-action")
async def zapier_action(payload: ZapierPayload):
    data = payload.dict()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(ZAPIER_WEBHOOK_URL, json=data)
            resp.raise_for_status()
            logger.info(f"Zapier webhook triggered with status {resp.status_code}")
            return {"status": "Zapier webhook triggered", "response": resp.json()}
    except httpx.HTTPError as e:
        logger.error(f"Error calling Zapier webhook: {e}")
        raise HTTPException(status_code=502, detail=f"Error calling Zapier webhook: {str(e)}")

@app.post("/memory/store")
async def memory_store(payload: MemoryStorePayload):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{MEMORY_AGENT_BASE_URL}/store", json=payload.dict())
            resp.raise_for_status()
            logger.info(f"Memory stored successfully, status {resp.status_code}")
            return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error forwarding to memory agent store: {e}")
        raise HTTPException(status_code=502, detail=f"Error forwarding to memory agent store: {str(e)}")

@app.post("/memory/retrieve")
async def memory_retrieve(payload: MemoryRetrievePayload):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{MEMORY_AGENT_BASE_URL}/retrieve", json=payload.dict())
            resp.raise_for_status()
            logger.info(f"Memory retrieved successfully, status {resp.status_code}")
            return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error forwarding to memory agent retrieve: {e}")
        raise HTTPException(status_code=502, detail=f"Error forwarding to memory agent retrieve: {str(e)}")
