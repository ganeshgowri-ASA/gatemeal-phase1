import streamlit as st
import json
import os

st.set_page_config(page_title="Resident Home - GateMeal", page_icon="🏠", layout="wide")

@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_data.json")
    with open(data_path, "r") as f:
        return json.load(f)

data = load_data()

# Auth check
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Please login from the Home page first.")
    st.page_link("app.py", label="← Go to Home")
    st.stop()

if st.session_state.role != "resident":
    st.error("🚫 Access denied. This page is for Residents only.")
    st.stop()

resident = next((r for r in data["residents"] if r["id"] == st.session_state.get("resident_id", "R001")), data["residents"][0])

# Header
st.markdown(f"""
<div style='background:linear-gradient(135deg,#FF6B35,#F7931E);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>🏠 Welcome, {resident['name']}!</h2>
    <p style='margin:0;'>📍 Flat {resident['flat']} | {resident['tower']} | 🥗 {resident['dietary']}</p>
</div>
""", unsafe_allow_html=True)

# My Orders summary
my_orders = [o for o in st.session_state.get("orders", data["orders"]) if o["resident_id"] == resident["id"]]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Total Orders", len(my_orders))
with col2:
    active = [o for o in my_orders if o["status"] not in ["Delivered", "Cancelled"]]
    st.metric("⏳ Active Orders", len(active))
with col3:
    delivered = [o for o in my_orders if o["status"] == "Delivered"]
    st.metric("✅ Delivered", len(delivered))
with col4:
    total_spend = sum(o["grand_total"] for o in my_orders)
    st.metric("💰 Total Spent", f"₹{total_spend}")

st.divider()

# Featured Kitchens
st.markdown("### 🌟 Featured Kitchens Today")
cols = st.columns(len(data["kitchens"]))
for i, kitchen in enumerate(data["kitchens"]):
    with cols[i]:
        status_color = "#22c55e" if kitchen["status"] == "Open" else "#ef4444"
        veg_badge = "🌱 Veg Only" if kitchen["veg_only"] else "🍖 Veg & Non-Veg"
        st.markdown(f"""
        <div style='background:white;border:1px solid #e5e7eb;border-radius:12px;padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:2.5rem'>🍳</div>
            <h4 style='margin:0.5rem 0 0.2rem;'>{kitchen['name']}</h4>
            <p style='color:#6b7280;font-size:0.85rem;margin:0;'>{kitchen['cuisine']}</p>
            <p style='color:#6b7280;font-size:0.8rem;margin:0.3rem 0;'>{veg_badge}</p>
            <p style='color:{status_color};font-weight:bold;margin:0.3rem 0;'>{kitchen['status']}</p>
            <p style='color:#374151;font-size:0.85rem;'>★ {kitchen['rating']} ({kitchen['reviews']} reviews)</p>
            <p style='color:#6b7280;font-size:0.8rem;'>⏰ {kitchen['timing']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

st.divider()

# Today's Popular Meals
st.markdown("### 🔥 Today's Popular Meals")

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    cat_filter = st.selectbox("🍽️ Category", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"])
with col_filter2:
    diet_filter = st.selectbox("🥗 Diet", ["All", "Veg Only", "Non-Veg"])

filtered_meals = [m for m in data["meals"] if m["available"]]
if cat_filter != "All":
    filtered_meals = [m for m in filtered_meals if m["category"] == cat_filter]
if diet_filter == "Veg Only":
    filtered_meals = [m for m in filtered_meals if m["veg"]]
elif diet_filter == "Non-Veg":
    filtered_meals = [m for m in filtered_meals if not m["veg"]]

if not filtered_meals:
    st.info("No meals found for selected filters.")
else:
    meal_cols = st.columns(3)
    for idx, meal in enumerate(filtered_meals[:6]):
        kitchen = next((k for k in data["kitchens"] if k["id"] == meal["kitchen_id"]), {})
        with meal_cols[idx % 3]:
            veg_icon = "🟢" if meal["veg"] else "🔴"
            st.markdown(f"""
            <div style='background:white;border:1px solid #e5e7eb;border-radius:10px;padding:1rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.05);'>
                <div style='font-size:2rem;text-align:center;'>{meal['image']}</div>
                <h4 style='margin:0.5rem 0 0.2rem;'>{veg_icon} {meal['name']}</h4>
                <p style='color:#6b7280;font-size:0.8rem;margin:0;'>🍳 {kitchen.get('name','')}</p>
                <p style='color:#6b7280;font-size:0.8rem;margin:0.2rem 0;'>🌶️ {meal['spice']} | ⏱ {meal['prep_time']}min | ★ {meal['rating']}</p>
                <p style='color:#FF6B35;font-weight:bold;font-size:1.1rem;margin:0.3rem 0;'>₹{meal['price']}</p>
                <p style='color:#374151;font-size:0.8rem;'>{meal['description'][:60]}...</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 Add to Cart", key=f"add_{meal['id']}"):
                if "cart" not in st.session_state:
                    st.session_state.cart = []
                existing = next((c for c in st.session_state.cart if c["meal_id"] == meal["id"]), None)
                if existing:
                    existing["qty"] += 1
                else:
                    st.session_state.cart.append({"meal_id": meal["id"], "name": meal["name"], "price": meal["price"], "qty": 1, "kitchen_id": meal["kitchen_id"]})
                st.success(f"✅ {meal['name']} added to cart!")

st.divider()

# Recent orders
st.markdown("### 📄 My Recent Orders")
if my_orders:
    for order in my_orders[-3:][::-1]:
        status_colors = {"Delivered": "🟢", "Preparing": "🟡", "Order Placed": "🔵", "Out for Delivery": "🟣"}
        icon = status_colors.get(order["status"], "⚪")
        with st.expander(f"{icon} {order['id']} | {order['kitchen_name']} | ₹{order['grand_total']} | {order['status']}"):
            items_str = ", ".join([f"{i['name']} x{i['qty']}" for i in order["items"]])
            st.write(f"**Items:** {items_str}")
            st.write(f"**Slot:** {order['slot']} | **Placed:** {order['placed_at']}")
            st.write(f"**OTP:** `{order['otp']}` | **Runner:** {order.get('runner') or 'Assigning...'}")
else:
    st.info("📦 No orders yet. Browse meals and place your first order!")
    st.page_link("pages/2_Browse_Meals.py", label="🔍 Browse Meals Now")

# Sidebar cart summary
with st.sidebar:
    st.markdown("## 🏠 Resident Panel")
    st.write(f"**{resident['name']}**")
    st.caption(f"Flat: {resident['flat']}")
    cart = st.session_state.get("cart", [])
    if cart:
        total_items = sum(c["qty"] for c in cart)
        st.info(f"🛒 Cart: {total_items} item(s)")
        st.page_link("pages/3_Cart_Checkout.py", label="➡️ Go to Cart & Checkout")
    st.divider()
    st.page_link("pages/2_Browse_Meals.py", label="🔍 Browse Meals")
    st.page_link("pages/4_Order_Tracking.py", label="📦 Track Orders")
