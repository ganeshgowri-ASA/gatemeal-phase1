import streamlit as st
import json
import os

st.set_page_config(page_title="Browse Meals - GateMeal", page_icon="🔍", layout="wide")

@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_data.json")
    with open(data_path, "r") as f:
        return json.load(f)

data = load_data()

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Please login from the Home page first.")
    st.page_link("app.py", label="← Go to Home")
    st.stop()

if "cart" not in st.session_state:
    st.session_state.cart = []

st.markdown("""
<div style='background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>🔍 Browse & Order Meals</h2>
    <p style='margin:0;'>Discover fresh home-cooked food from your community kitchens</p>
</div>
""", unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    search = st.text_input("🔎 Search meals...", placeholder="e.g. Dosa, Curry...")
with col2:
    category = st.selectbox("🍽️ Category", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"])
with col3:
    kitchen_filter = st.selectbox("🍳 Kitchen", ["All"] + [k["name"] for k in data["kitchens"]])
with col4:
    diet = st.selectbox("🥗 Diet", ["All", "Veg Only", "Non-Veg"])

col5, col6 = st.columns(2)
with col5:
    price_max = st.slider("💰 Max Price (₹)", 50, 300, 300, 10)
with col6:
    spice = st.selectbox("🌶️ Spice Level", ["All", "Mild", "Medium", "Hot"])

# Apply filters
meals = data["meals"]
if search:
    meals = [m for m in meals if search.lower() in m["name"].lower() or search.lower() in m["description"].lower()]
if category != "All":
    meals = [m for m in meals if m["category"] == category]
if kitchen_filter != "All":
    kitchen_id = next((k["id"] for k in data["kitchens"] if k["name"] == kitchen_filter), None)
    if kitchen_id:
        meals = [m for m in meals if m["kitchen_id"] == kitchen_id]
if diet == "Veg Only":
    meals = [m for m in meals if m["veg"]]
elif diet == "Non-Veg":
    meals = [m for m in meals if not m["veg"]]
meals = [m for m in meals if m["price"] <= price_max]
if spice != "All":
    meals = [m for m in meals if m["spice"] == spice]

st.markdown(f"**{len(meals)} meals found**")
st.divider()

if not meals:
    st.info("😔 No meals match your filters. Try adjusting them.")
else:
    cols = st.columns(3)
    for idx, meal in enumerate(meals):
        kitchen = next((k for k in data["kitchens"] if k["id"] == meal["kitchen_id"]), {})
        with cols[idx % 3]:
            veg_icon = "🟢" if meal["veg"] else "🔴"
            avail_text = "✅ Available" if meal["available"] else "❌ Unavailable"
            avail_color = "#22c55e" if meal["available"] else "#ef4444"
            st.markdown(f"""
            <div style='background:white;border:1px solid #e5e7eb;border-radius:12px;padding:1.2rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
                <div style='font-size:2.5rem;text-align:center;'>{meal['image']}</div>
                <h4 style='margin:0.5rem 0 0.2rem;'>{veg_icon} {meal['name']}</h4>
                <p style='color:#6b7280;font-size:0.82rem;margin:0;'>🍳 {kitchen.get('name','')} &nbsp;|&nbsp; {meal['category']}</p>
                <p style='color:#6b7280;font-size:0.82rem;margin:0.3rem 0;'>🌶️ {meal['spice']} &nbsp;|⏱ {meal['prep_time']} min &nbsp;|★ {meal['rating']}</p>
                <p style='color:{avail_color};font-size:0.8rem;font-weight:bold;'>{avail_text}</p>
                <p style='color:#374151;font-size:0.82rem;'>{meal['description']}</p>
                <p style='color:#FF6B35;font-weight:bold;font-size:1.2rem;margin:0.5rem 0 0;'>₹{meal['price']}</p>
            </div>
            """, unsafe_allow_html=True)

            if meal["available"]:
                qty = st.number_input("Qty", min_value=1, max_value=10, value=1, key=f"qty_{meal['id']}")
                if st.button(f"🛒 Add to Cart", key=f"add_{meal['id']}", use_container_width=True):
                    existing = next((c for c in st.session_state.cart if c["meal_id"] == meal["id"]), None)
                    if existing:
                        existing["qty"] += qty
                    else:
                        st.session_state.cart.append({
                            "meal_id": meal["id"],
                            "name": meal["name"],
                            "price": meal["price"],
                            "qty": qty,
                            "kitchen_id": meal["kitchen_id"],
                            "kitchen_name": kitchen.get("name", "")
                        })
                    st.success(f"✅ {meal['name']} x{qty} added!")
                    st.rerun()
            else:
                st.button("🚫 Unavailable", key=f"na_{meal['id']}", disabled=True, use_container_width=True)

# Sidebar cart
with st.sidebar:
    st.markdown("## 🛒 Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.caption("Your cart is empty.")
    else:
        total = 0
        for item in cart:
            st.write(f"• {item['name']} x{item['qty']} = ₹{item['price']*item['qty']}")
            total += item['price'] * item['qty']
        st.divider()
        st.write(f"**Subtotal: ₹{total}**")
        st.write(f"**Delivery: ₹20**")
        st.write(f"**Total: ₹{total+20}**")
        st.divider()
        if st.button("🧹 Clear Cart"):
            st.session_state.cart = []
            st.rerun()
        st.page_link("pages/3_Cart_Checkout.py", label="➡️ Proceed to Checkout")
