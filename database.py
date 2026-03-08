import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_conn()
    cur  = conn.cursor()

    # ── MENU ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id          SERIAL PRIMARY KEY,
            name        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            price       INTEGER NOT NULL,
            category    TEXT    NOT NULL,
            image_url   TEXT    NOT NULL,
            active      BOOLEAN DEFAULT TRUE,
            created_at  TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── ORDERS ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id           TEXT PRIMARY KEY,
            customer_phone TEXT NOT NULL,
            payment_type TEXT NOT NULL,
            total        INTEGER NOT NULL,
            items        JSONB   NOT NULL,
            created_at   TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── OFFERS ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id         SERIAL PRIMARY KEY,
            title      TEXT NOT NULL,
            description TEXT NOT NULL,
            tag        TEXT,
            valid_until DATE,
            color      TEXT DEFAULT 'gold',
            status     TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── SETTINGS ──────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Seed default settings
    cur.execute("""
        INSERT INTO settings (key, value) VALUES
            ('wa_number', '918320847041'),
            ('upi_id',    ''),
            ('qr_img',    '')
        ON CONFLICT (key) DO NOTHING
    """)

    # Seed default menu if empty
    cur.execute("SELECT COUNT(*) as cnt FROM menu")
    row = cur.fetchone()
    if row["cnt"] == 0:
        default_items = [
            ("Plain Soda",                    "Refreshing plain soda",        20,  "Soda",             "https://media.istockphoto.com/id/1181609421/photo/glass-of-carbonated-water-with-ice.jpg?s=612x612&w=0&k=20&c=s265A-SmZcoT4iV3IITrMEbTjISFhmC9NBBh8n14sGg="),
            ("Nimbu Soda",                    "Refreshing lemon soda",         20,  "Soda",             "https://binjalsvegkitchen.com/wp-content/uploads/2016/03/Nimbu-Masala-Soda-H1.jpg"),
            ("Sweet Soda",                    "Refreshing sweet soda",         20,  "Soda",             "https://images.jdmagicbox.com/quickquotes/images_main/sweet-lime-soda-sweet-and-salty-soft-drinks-200ml-2224527146-t7mpwol9.jpg"),
            ("Cold Coco Shake",               "Rich creamy chocolate shake",   50,  "Milk Shake",       "https://www.temptingtreat.com/wp-content/uploads/2025/07/cold-coco-p1-1140x1425.jpg"),
            ("Strawberry Smoothie",           "Fresh fruit blend",             80,  "Smoothie",         "https://foodsharingvegan.com/wp-content/uploads/2022/03/Strawberry-Yogurt-Smoothie-Plant-Based-on-a-Budget-1-2.jpg"),
            ("Mint Mojito",                   "Sweet & tangy classic",         50,  "Mojito",           "https://www.foodandwine.com/thmb/e8AvEfBBfwjg3xmt6E__rRvSZlA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Mojito-FT-RECIPE1022-2000-85cdb1eb59454847b713713e32e365c0.jpg"),
            ("Mix Fruit Juice",               "Fresh mixed fruit blend",       80,  "Juice",            "https://images.unsplash.com/photo-1622597467836-f3e6b8a3a3b5?w=500"),
            ("Butterscotch Korean Ice Cream", "Feel Butterscotch",             80,  "Korean Ice Cream", "https://content.jdmagicbox.com/v2/comp/noida/p7/011pxx11.xx11.240817020135.v4p7/catalogue/bingsu-ice-cream-noida-ice-cream-parlours-stbets7st8.jpg"),
            ("Rose Faluda",                   "Classic Indian dessert drink",  90,  "Faluda",           "https://images.unsplash.com/photo-1571771680986-6f9f498ebdb7?w=500"),
            ("Cold Coffee",                   "Chilled creamy coffee",         60,  "Coffee",           "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=500"),
            ("Mango Slushy",                  "Icy mango chill",               70,  "Slushy",           "https://images.unsplash.com/photo-1546549032-9571cd6b27df?w=500"),
            ("Vanilla Latte",                 "Smooth & creamy latte",         75,  "Latte",            "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=500"),
            ("Watermelon Mojito",             "Summer special",                60,  "Mojito",           "https://images.unsplash.com/photo-1497534446932-c925b458314e?w=500"),
            ("Blue Lagoon Soda",              "Tangy blue fizzy drink",        40,  "Soda",             "https://images.unsplash.com/photo-1541658016709-82535e94bc69?w=500"),
        ]
        cur.executemany("""
            INSERT INTO menu (name, description, price, category, image_url)
            VALUES (%s, %s, %s, %s, %s)
        """, default_items)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ DB initialized!")
