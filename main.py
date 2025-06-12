from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from contextlib import asynccontextmanager

# Define lifespan handler for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create SQLite database and table
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    yield
    # Shutdown: nothing to clean up for SQLite

# Pass lifespan to FastAPI
app = FastAPI(lifespan=lifespan)

# Data model for demonstration
class FoodItem(BaseModel):
    id: int | None = None
    name: str
    calories: int

@app.get("/")
def read_root():
    return {"message": "Hello, Nutrition API!"}

@app.post("/foods/")
def create_food(item: FoodItem):
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO foods (name, calories) VALUES (?, ?) RETURNING id",
        (item.name, item.calories)
    )
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return {"id": row[0], "name": item.name, "calories": item.calories}

@app.get("/foods/{food_id}")
def read_food(food_id: int):
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, calories FROM foods WHERE id = ?",
        (food_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "calories": row[2]}
    return {"error": "Food not found"}

# To run:
# uvicorn main:app --reload --port 8000