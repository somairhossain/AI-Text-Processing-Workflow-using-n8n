from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl
import httpx
import uuid
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
if not N8N_WEBHOOK_URL:
    raise RuntimeError("N8N_WEBHOOK_URL must be set in backend/.env or the environment")

app = FastAPI(
    title="AI Text Processing Backend",
    description="Receives user input and forwards it to an n8n webhook with a session ID.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessTextRequest(BaseModel):
    email: EmailStr
    text: str

class ProcessUrlRequest(BaseModel):
    email: EmailStr
    url: HttpUrl

async def send_to_n8n(payload: dict) -> None:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(N8N_WEBHOOK_URL, json=payload)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=502, detail=f"n8n webhook failed: {exc.response.text}")

@app.post("/process")
async def process(data: ProcessTextRequest):
    session_id = uuid.uuid4().hex[:8]
    payload = {"email": data.email, "text": data.text, "session_id": session_id}
    await send_to_n8n(payload)
    return {"status": "sent", "session_id": session_id}

@app.post("/process-url")
async def process_url(data: ProcessUrlRequest):
    session_id = uuid.uuid4().hex[:8]
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(str(data.url))
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc.response.text}")

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
    if not page_text:
        raise HTTPException(status_code=400, detail="Could not extract paragraph text from the URL.")

    payload = {
        "email": data.email,
        "text": page_text,
        "session_id": session_id,
        "source_url": str(data.url),
    }
    await send_to_n8n(payload)
    return {"status": "sent", "session_id": session_id}
