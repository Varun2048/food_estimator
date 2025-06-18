from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chat_agent import qa_chain, memory

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

app = FastAPI(title="Food Chat API")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = qa_chain({"question": req.message})
        return ChatResponse(answer=result["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def history():
    # returns list of {"role": ..., "content": ...}
    return [{"role": m.type, "content": m.content} for m in memory.chat_memory.messages]

# app.py (below your existing POST /chat)

@app.get("/chat", response_model=ChatResponse)
def chat_get(message: str):
    """
    Query the chat agent via GET for quick tests.
    Example: /chat?message=Which%20foods%20are%20high%20in%20protein%3F
    """
    try:
        result = qa_chain({"question": message})
        return ChatResponse(answer=result["answer"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
