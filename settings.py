from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import hashlib
from database import get_conn

router = APIRouter(prefix="/api/settings", tags=["settings"])

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()

class ShopSettings(BaseModel):
    wa_number: Optional[str] = ""
    upi_id:    Optional[str] = ""
    qr_img:    Optional[str] = ""

class Credentials(BaseModel):
    username:     str
    new_password: str

class LoginCheck(BaseModel):
    username: str
    password: str

# ── GET all settings ───────────────────────────────────────────
@router.get("/")
def get_settings():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT key, value FROM settings")
    rows = cur.fetchall()
    cur.close(); conn.close()
    data = {r["key"]: r["value"] for r in rows}
    # Never return password hash to frontend
    data.pop("admin_pass", None)
    data.pop("admin_user", None)
    return data

# ── POST check admin login ─────────────────────────────────────
@router.post("/login")
def check_login(creds: LoginCheck):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='admin_user'")
    user_row = cur.fetchone()
    cur.execute("SELECT value FROM settings WHERE key='admin_pass'")
    pass_row = cur.fetchone()
    cur.close(); conn.close()

    # Default creds if not set yet
    stored_user = user_row["value"] if user_row else "admin"
    stored_pass = pass_row["value"] if pass_row else hash_pass("admin@123")

    if creds.username == stored_user and hash_pass(creds.password) == stored_pass:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Wrong credentials")

# ── PUT update shop settings ───────────────────────────────────
@router.put("/shop")
def update_shop_settings(s: ShopSettings):
    conn = get_conn()
    cur  = conn.cursor()
    for key, val in [("wa_number", s.wa_number), ("upi_id", s.upi_id), ("qr_img", s.qr_img)]:
        cur.execute("""
            INSERT INTO settings (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, (key, val))
    conn.commit(); cur.close(); conn.close()
    return {"updated": True}

# ── PUT update admin credentials ──────────────────────────────
@router.put("/credentials")
def update_credentials(creds: Credentials):
    conn = get_conn()
    cur  = conn.cursor()
    hashed = hash_pass(creds.new_password)
    for key, val in [("admin_user", creds.username), ("admin_pass", hashed)]:
        cur.execute("""
            INSERT INTO settings (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, (key, val))
    conn.commit(); cur.close(); conn.close()
    return {"updated": True}
