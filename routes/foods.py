from fastapi import APIRouter
import sqlite3

router = APIRouter()

@router.get("/foods")
def get_foods():
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, calories FROM foods")
    rows = cursor.fetchall()
    conn.close()
    return {"foods": [{"id": r[0], "name": r[1], "calories": r[2]} for r in rows]}
