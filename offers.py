from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter(prefix="/api/offers", tags=["offers"])

class Offer(BaseModel):
    title:       str
    description: str
    tag:         Optional[str] = ""
    valid_until: Optional[str] = None
    color:       Optional[str] = "gold"
    status:      Optional[str] = "active"

# ── GET active offers (for customers) ─────────────────────────
@router.get("/")
def get_active_offers():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM offers
        WHERE status = 'active'
        AND (valid_until IS NULL OR valid_until >= CURRENT_DATE)
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

# ── GET all offers (for admin) ─────────────────────────────────
@router.get("/all")
def get_all_offers():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM offers ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["valid_until"] = str(d["valid_until"]) if d["valid_until"] else ""
        result.append(d)
    return result

# ── POST add offer ─────────────────────────────────────────────
@router.post("/")
def add_offer(offer: Offer):
    conn = get_conn()
    cur  = conn.cursor()
    valid = offer.valid_until if offer.valid_until else None
    cur.execute("""
        INSERT INTO offers (title, description, tag, valid_until, color, status)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
    """, (offer.title, offer.description, offer.tag, valid, offer.color, offer.status))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    d = dict(row)
    d["valid_until"] = str(d["valid_until"]) if d["valid_until"] else ""
    return d

# ── PUT update offer ───────────────────────────────────────────
@router.put("/{offer_id}")
def update_offer(offer_id: int, offer: Offer):
    conn = get_conn()
    cur  = conn.cursor()
    valid = offer.valid_until if offer.valid_until else None
    cur.execute("""
        UPDATE offers SET title=%s, description=%s, tag=%s,
        valid_until=%s, color=%s, status=%s
        WHERE id=%s RETURNING *
    """, (offer.title, offer.description, offer.tag, valid, offer.color, offer.status, offer_id))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Offer not found")
    d = dict(row)
    d["valid_until"] = str(d["valid_until"]) if d["valid_until"] else ""
    return d

# ── PATCH toggle status ────────────────────────────────────────
@router.patch("/{offer_id}/toggle")
def toggle_offer(offer_id: int):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE offers
        SET status = CASE WHEN status='active' THEN 'inactive' ELSE 'active' END
        WHERE id=%s RETURNING id, status
    """, (offer_id,))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Offer not found")
    return dict(row)

# ── DELETE offer ───────────────────────────────────────────────
@router.delete("/{offer_id}")
def delete_offer(offer_id: int):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM offers WHERE id=%s RETURNING id", (offer_id,))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Offer not found")
    return {"deleted": offer_id}
