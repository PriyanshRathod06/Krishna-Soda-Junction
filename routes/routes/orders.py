from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
from database import get_conn

router = APIRouter(prefix="/api/orders", tags=["orders"])

class OrderItem(BaseModel):
    name:  str
    qty:   int
    price: int
    sub:   int

class Order(BaseModel):
    id:             str
    customer_phone: str
    payment_type:   str
    total:          int
    items:          List[OrderItem]

@router.post("/")
def save_order(order: Order):
    conn = get_conn()
    cur  = conn.cursor()
    items_json = json.dumps([i.dict() for i in order.items])
    cur.execute("""
        INSERT INTO orders (id, customer_phone, payment_type, total, items)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        RETURNING *
    """, (order.id, order.customer_phone, order.payment_type, order.total, items_json))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return {"saved": True, "order_id": order.id}

@router.get("/")
def get_orders():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = d["items"] if isinstance(d["items"], list) else json.loads(d["items"])
        d["created_at"] = d["created_at"].strftime("%d/%m/%y, %I:%M %p") if d["created_at"] else ""
        result.append(d)
    return result

@router.get("/today")
def get_today_orders():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM orders
        WHERE DATE(created_at AT TIME ZONE 'Asia/Kolkata') = CURRENT_DATE AT TIME ZONE 'Asia/Kolkata'
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = d["items"] if isinstance(d["items"], list) else json.loads(d["items"])
        d["created_at"] = d["created_at"].strftime("%d/%m/%y, %I:%M %p") if d["created_at"] else ""
        result.append(d)
    return result

@router.get("/analytics")
def get_analytics():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as rev FROM orders")
    total_row = cur.fetchone()
    cur.execute("""
        SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as rev FROM orders
        WHERE DATE(created_at AT TIME ZONE 'Asia/Kolkata') = CURRENT_DATE AT TIME ZONE 'Asia/Kolkata'
    """)
    today_row = cur.fetchone()
    cur.execute("""
        SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as rev FROM orders
        WHERE DATE(created_at AT TIME ZONE 'Asia/Kolkata') =
              (CURRENT_DATE AT TIME ZONE 'Asia/Kolkata') - INTERVAL '1 day'
    """)
    yest_row = cur.fetchone()
    cur.execute("""
        SELECT payment_type, COUNT(*) as cnt, COALESCE(SUM(total),0) as rev
        FROM orders GROUP BY payment_type
    """)
    pay_rows = cur.fetchall()
    cur.execute("""
        SELECT DATE(created_at AT TIME ZONE 'Asia/Kolkata') as day,
               COUNT(*) as cnt, COALESCE(SUM(total),0) as rev
        FROM orders WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY day ORDER BY day
    """)
    week_rows = cur.fetchall()
    cur.execute("SELECT items FROM orders")
    all_orders = cur.fetchall()
    cur.close(); conn.close()
    item_qty = {}; item_rev = {}; item_cnt = {}
    for row in all_orders:
        items = row["items"] if isinstance(row["items"], list) else json.loads(row["items"])
        for it in items:
            n = it["name"]
            item_qty[n] = item_qty.get(n, 0) + it["qty"]
            item_rev[n] = item_rev.get(n, 0) + it["sub"]
            item_cnt[n] = item_cnt.get(n, 0) + 1
    top_products = sorted(
        [{"name": k, "qty": item_qty[k], "revenue": item_rev[k], "orders": item_cnt[k]} for k in item_qty],
        key=lambda x: x["qty"], reverse=True
    )[:10]
    pay_map = {r["payment_type"]: {"count": r["cnt"], "revenue": r["rev"]} for r in pay_rows}
    return {
        "total":     {"orders": total_row["cnt"], "revenue": total_row["rev"]},
        "today":     {"orders": today_row["cnt"], "revenue": today_row["rev"]},
        "yesterday": {"orders": yest_row["cnt"],  "revenue": yest_row["rev"]},
        "by_payment": pay_map,
        "last_7_days": [{"day": str(r["day"]), "orders": r["cnt"], "revenue": r["rev"]} for r in week_rows],
        "top_products": top_products,
    }

@router.delete("/all")
def clear_all_orders():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM orders")
    conn.commit(); cur.close(); conn.close()
    return {"cleared": True}
