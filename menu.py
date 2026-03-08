from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter(prefix="/api/menu", tags=["menu"])

class MenuItem(BaseModel):
    name:        str
    description: str
    price:       int
    category:    str
    image_url:   str
    active:      Optional[bool] = True

# ── GET all menu items ─────────────────────────────────────────
@router.get("/")
def get_menu():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM menu WHERE active = TRUE ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

# ── GET all (including inactive) — admin only ──────────────────
@router.get("/all")
def get_menu_all():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM menu ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

# ── POST add new item ──────────────────────────────────────────
@router.post("/")
def add_menu_item(item: MenuItem):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO menu (name, description, price, category, image_url, active)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (item.name, item.description, item.price, item.category, item.image_url, item.active))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return dict(row)

# ── PUT update item ────────────────────────────────────────────
@router.put("/{item_id}")
def update_menu_item(item_id: int, item: MenuItem):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE menu
        SET name=%s, description=%s, price=%s, category=%s, image_url=%s, active=%s
        WHERE id=%s RETURNING *
    """, (item.name, item.description, item.price, item.category, item.image_url, item.active, item_id))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(row)

# ── DELETE item ────────────────────────────────────────────────
@router.delete("/{item_id}")
def delete_menu_item(item_id: int):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM menu WHERE id=%s RETURNING id", (item_id,))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": item_id}
