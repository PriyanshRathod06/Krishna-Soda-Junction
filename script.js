/* ══════════════════════════════════════════════════════════════
   KRISHNA SODA JUNCTION — script.js
   Backend: FastAPI + PostgreSQL on Railway
   ══════════════════════════════════════════════════════════════ */

// ── CONFIG — replace with your Railway URL after deploy ───────
let menu      = [];
let cart      = {};
let activeCat = "All";

// ── API HELPER ─────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error("API error:", e);
    return null;
  }
}

// ── LOAD MENU ──────────────────────────────────────────────────
async function loadMenu() {
  const data = await apiFetch("/api/menu/");
  if (data) {
    menu = data.map(item => ({
      id: item.id, name: item.name, desc: item.description,
      price: item.price, cat: item.category, img: item.image_url,
    }));
  }
  renderProducts();
}

// ── OFFER BANNERS ──────────────────────────────────────────────
async function renderOfferBanners() {
  const wrap = document.getElementById("offer-banners");
  if (!wrap) return;
  const offers = await apiFetch("/api/offers/");
  if (!offers || offers.length === 0) { wrap.innerHTML = ""; return; }

  const COLORS = {
    gold:   { bg:"rgba(245,197,24,0.12)",  border:"rgba(245,197,24,0.4)",  text:"#f5c518" },
    green:  { bg:"rgba(46,204,113,0.12)",  border:"rgba(46,204,113,0.4)",  text:"#2ecc71" },
    red:    { bg:"rgba(231,76,60,0.12)",   border:"rgba(231,76,60,0.4)",   text:"#e74c3c" },
    blue:   { bg:"rgba(52,152,219,0.12)",  border:"rgba(52,152,219,0.4)",  text:"#3498db" },
    purple: { bg:"rgba(155,89,182,0.12)",  border:"rgba(155,89,182,0.4)",  text:"#9b59b6" },
  };
  const EMOJIS = { gold:"🎁", green:"🌿", red:"🔥", blue:"💙", purple:"💜" };

  wrap.innerHTML = offers.map(o => {
    const c = COLORS[o.color] || COLORS.gold;
    const emoji = EMOJIS[o.color] || "🎁";
    const valid = o.valid_until ? ` &nbsp;📅 Till ${new Date(o.valid_until).toLocaleDateString("en-IN")}` : "";
    return `
      <div class="offer-banner" style="background:${c.bg};border-color:${c.border}">
        <div class="ob-left">
          <span class="ob-emoji">${emoji}</span>
          <div class="ob-text">
            <div class="ob-title" style="color:${c.text}">${o.title}</div>
            <div class="ob-desc">${o.description}${valid}</div>
          </div>
        </div>
        ${o.tag ? `<div class="ob-tag" style="background:${c.text};color:#000">${o.tag}</div>` : ""}
      </div>`;
  }).join("");
}

// ── RENDER PRODUCTS ────────────────────────────────────────────
function renderProducts() {
  const query = document.getElementById("search-input").value.trim().toLowerCase();
  const grid  = document.getElementById("products-grid");
  const noRes = document.getElementById("no-results");

  const filtered = menu.filter(item => {
    const matchCat  = activeCat === "All" || item.cat === activeCat;
    const matchText = item.name.toLowerCase().includes(query) || item.desc.toLowerCase().includes(query);
    return matchCat && matchText;
  });

  grid.innerHTML = "";
  noRes.style.display = filtered.length ? "none" : "block";

  filtered.forEach(item => {
    const qty = cart[item.id] || 0;
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="card-img-wrap">
        <img src="${item.img}" alt="${item.name}" loading="lazy"
             onerror="this.src='https://placehold.co/400x300/111111/f5c518?text=🥤'" />
      </div>
      <div class="card-body">
        <h3>${item.name}</h3>
        <p>${item.desc}</p>
        <div class="card-footer">
          <span class="price">₹${item.price}</span>
          <div id="ctrl-${item.id}">
            ${qty === 0
              ? `<button class="add-btn" onclick="addToCart(${item.id})">+ Add</button>`
              : `<div class="qty-ctrl">
                   <button onclick="changeQty(${item.id},-1)">−</button>
                   <span>${qty}</span>
                   <button onclick="changeQty(${item.id},1)">+</button>
                 </div>`}
          </div>
        </div>
      </div>`;
    grid.appendChild(card);
  });
}

// ── CART ───────────────────────────────────────────────────────
function addToCart(id)  { cart[id] = 1; updateUI(); }
function changeQty(id, delta) {
  const n = (cart[id] || 0) + delta;
  if (n <= 0) delete cart[id]; else cart[id] = n;
  updateUI();
}
function clearCart() { cart = {}; updateUI(); }
function updateUI()  { renderProducts(); renderCartPanel(); updateCartBadge(); }

function updateCartBadge() {
  const total = Object.values(cart).reduce((a, b) => a + b, 0);
  const badge = document.getElementById("cart-count");
  badge.textContent   = total;
  badge.style.display = total > 0 ? "flex" : "none";
}

function renderCartPanel() {
  const list    = document.getElementById("cart-items-list");
  const totalEl = document.getElementById("cart-total");
  const keys    = Object.keys(cart).filter(k => cart[k] > 0);
  if (keys.length === 0) {
    list.innerHTML = `<p class="cart-empty">Your cart is empty 🥤</p>`;
    totalEl.textContent = "₹0";
    return;
  }
  let grand = 0;
  list.innerHTML = keys.map(id => {
    const item = menu.find(m => m.id == id);
    if (!item) return "";
    const sub = item.price * cart[id];
    grand += sub;
    return `<div class="cart-item">
      <div class="cart-item-info"><h4>${item.name} × ${cart[id]}</h4><span>₹${sub}</span></div>
      <div class="qty-ctrl" style="margin-right:4px">
        <button onclick="changeQty(${item.id},-1)">−</button>
        <span>${cart[id]}</span>
        <button onclick="changeQty(${item.id},1)">+</button>
      </div>
      <button class="cart-item-remove" onclick="changeQty(${item.id},-${cart[id]})">✕</button>
    </div>`;
  }).join("");
  totalEl.textContent = `₹${grand}`;
}

function toggleCart() {
  document.getElementById("cart-overlay").classList.toggle("open");
  document.getElementById("cart-panel").classList.toggle("open");
}

// ── CHECKOUT ───────────────────────────────────────────────────
async function openCheckout() {
  const keys = Object.keys(cart).filter(k => cart[k] > 0);
  if (keys.length === 0) { alert("Cart is empty! 🛒"); return; }

  let grand = 0;
  const rows = keys.map(id => {
    const item = menu.find(m => m.id == id);
    const sub  = item.price * cart[id]; grand += sub;
    return `<div class="co-item-row"><span>${item.name} × ${cart[id]}</span><span>₹${sub}</span></div>`;
  }).join("");

  document.getElementById("co-summary").innerHTML = rows;
  document.getElementById("co-total").textContent = `₹${grand}`;
  document.getElementById("co-phone").value = "";
  document.querySelector('input[name="pay"][value="Cash"]').checked = true;
  document.getElementById("qr-section").style.display = "none";

  const s = await apiFetch("/api/settings/");
  if (s?.qr_img) document.getElementById("qr-img").src = s.qr_img;
  document.getElementById("qr-upi-note").textContent = s?.upi_id ? `UPI: ${s.upi_id}` : "";

  document.getElementById("checkout-overlay").classList.add("open");
  document.getElementById("checkout-modal").classList.add("open");
  document.getElementById("cart-overlay").classList.remove("open");
  document.getElementById("cart-panel").classList.remove("open");
}

function closeCheckout() {
  document.getElementById("checkout-overlay").classList.remove("open");
  document.getElementById("checkout-modal").classList.remove("open");
}

async function onPayChange() {
  const val = document.querySelector('input[name="pay"]:checked').value;
  const qrSec = document.getElementById("qr-section");
  if (val === "Online") {
    const s = await apiFetch("/api/settings/");
    document.getElementById("qr-img").src = s?.qr_img || "https://placehold.co/200x200/1a1a1a/f5c518?text=Set+QR+in+Admin";
    document.getElementById("qr-upi-note").textContent = s?.upi_id ? `UPI ID: ${s.upi_id}` : "";
    qrSec.style.display = "block";
  } else {
    qrSec.style.display = "none";
  }
}

async function placeOrder() {
  const phone   = document.getElementById("co-phone").value.trim();
  const payment = document.querySelector('input[name="pay"]:checked').value;
  if (!phone || phone.length < 10) { alert("Valid 10-digit WhatsApp number chahiye! 📱"); return; }

  const keys = Object.keys(cart).filter(k => cart[k] > 0);
  let grand = 0;
  const items = keys.map(id => {
    const item = menu.find(m => m.id == id);
    const sub = item.price * cart[id]; grand += sub;
    return { name: item.name, qty: cart[id], price: item.price, sub };
  });

  const orderId = "ORD" + Date.now().toString().slice(-6);
  const timeStr = new Date().toLocaleString("en-IN", { dateStyle:"short", timeStyle:"short" });

  // Save to DB
  await apiFetch("/api/orders/", {
    method: "POST",
    body: JSON.stringify({ id: orderId, customer_phone: "91"+phone, payment_type: payment, total: grand, items }),
  });

  // Get settings for WA + QR
  const s = await apiFetch("/api/settings/");
  const shopWA = s?.wa_number || "918320847041";
  const qrImg  = s?.qr_img || "";
  const upiId  = s?.upi_id || "";

  // Customer bill
  let msg = `🥤 *Krishna Soda Junction*\n📋 *Order ID: ${orderId}*\n📅 ${timeStr}\n━━━━━━━━━━━━━━━━\n`;
  items.forEach(i => { msg += `• ${i.name} × ${i.qty} = ₹${i.sub}\n`; });
  msg += `━━━━━━━━━━━━━━━━\n💰 *Total: ₹${grand}*\n💳 Payment: *${payment}*\n\n`;
  if (payment === "Online" && upiId) msg += `📲 UPI: *${upiId}*\n`;
  msg += `✅ Thank you!\n🏪 Krishna Soda Junction, Ahmedabad`;

  window.open(`https://wa.me/91${phone}?text=${encodeURIComponent(msg)}`, "_blank");

  // Owner notification
  let ownerMsg = `🔔 *New Order!*\n📋 ${orderId}\n📱 +91${phone}\n━━━━━━━━━━━━━━━━\n`;
  items.forEach(i => { ownerMsg += `• ${i.name} × ${i.qty} = ₹${i.sub}\n`; });
  ownerMsg += `━━━━━━━━━━━━━━━━\n💰 *₹${grand}* | 💳 ${payment}`;
  setTimeout(() => window.open(`https://wa.me/${shopWA}?text=${encodeURIComponent(ownerMsg)}`, "_blank"), 800);

  if (payment === "Online" && qrImg) {
    const qrMsg = `🧾 *QR for Order ${orderId}*\n\nPay ₹${grand}:\n${qrImg}`;
    setTimeout(() => window.open(`https://wa.me/91${phone}?text=${encodeURIComponent(qrMsg)}`, "_blank"), 1600);
  }

  cart = {}; updateUI(); closeCheckout();
}

// ── FILTER / CATEGORY ──────────────────────────────────────────
function filterProducts() { renderProducts(); }
function setCategory(btn) {
  document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  activeCat = btn.dataset.cat;
  renderProducts();
}

// ── INIT ───────────────────────────────────────────────────────
window.addEventListener("load", async () => {
  await Promise.all([loadMenu(), renderOfferBanners()]);
  setTimeout(() => {
    const loader = document.getElementById("loader");
    loader.classList.add("hide");
    setTimeout(() => (loader.style.display = "none"), 500);
  }, 1000);
});
