from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from food_agent import generate_caption, get_context_from_chroma, get_answer

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Session store
session_store = {}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("index.html")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    session_id = str(uuid4())
    ext = file.filename.split(".")[-1]
    image_path = os.path.join(UPLOAD_DIR, f"{session_id}.{ext}")

    with open(image_path, "wb") as f:
        f.write(await file.read())

    caption = generate_caption(image_path)

    session_store[session_id] = {
        "caption": caption,
        "image_path": image_path
    }

    return {
        "session_id": session_id,
        "caption": caption,
        "image_url": f"/images/{session_id}.{ext}"
    }

@app.post("/ask")
async def ask(session_id: str = Form(...), question: str = Form(...)):
    session = session_store.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    caption = session["caption"]
    context = get_context_from_chroma(caption, question)
    answer = get_answer(caption, context, question)

    # Save history
    session.setdefault("history", []).append({
        "question": question,
        "answer": answer
    })

    return {"answer": answer}

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    session = session_store.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    return {"history": session.get("history", [])}