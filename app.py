from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import menu, orders, offers, settings

app = FastAPI(title="Krishna Soda Junction API", version="1.0.0")

# ── CORS — allow GitHub Pages frontend ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # After deploy: replace with your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include all routers ────────────────────────────────────────
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(offers.router)
app.include_router(settings.router)

# ── Startup: init DB tables ────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()

# ── Health check ───────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "app": "Krishna Soda Junction API 🥤"}

@app.get("/health")
def health():
    return {"status": "healthy"}
