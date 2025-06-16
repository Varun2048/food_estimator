from fastapi import FastAPI
from db import init_db
from routes.foods import router as foods_router

app = FastAPI(lifespan=init_db)

@app.get("/")
def read_root():
    return {"message": "Hello World with SQLite!"}

# Register food routes
app.include_router(foods_router)