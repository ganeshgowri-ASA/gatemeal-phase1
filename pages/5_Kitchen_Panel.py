import streamlit as st
import json
import os

st.set_page_config(page_title="Kitchen Panel - GateMeal", page_icon="👨‍🍳", layout="wide")

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

if st.session_state.role not in ["kitchen", "admin"]:
    st.error("🚫 Access denied. This page is for Kitchen Partners only.")
    st.stop()

if "orders" not in st.session_state:
    st.session_state.orders = data["orders"]

kitchen_id = st.session_state.get("kitchen_id", "K001")
kitchen = next((k for k in data["kitchens"] if k["id"] == kitchen_id), data["kitchens"][0])

st.markdown(f"""
<div style='background:linear-gradient(135deg,#dc2626,#ef4444);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>👨‍🍳 Kitchen Panel: {kitchen['name']}</h2>
    <p style='margin:0;'>🍽️ {kitchen['cuisine']} | ⏰ {kitchen['timing']} | Owner: {kitchen['owner']}</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📥 Incoming Orders", "📊 Analytics", "📖 My Menu", "⚙️ Kitchen Settings"])

with tab1:
    st.markdown("### 📥 Incoming Orders")
    
    kitchen_orders = [o for o in st.session_state.orders if o["kitchen_id"] == kitchen_id]
    
    STATUS_FLOW = ["Order Placed", "Accepted", "Preparing", "Ready for Pickup", "Out for Delivery", "Delivered"]
    
    active_orders = [o for o in kitchen_orders if o["status"] not in ["Delivered", "Cancelled"]]
    delivered_orders = [o for o in kitchen_orders if o["status"] == "Delivered"]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📥 New Orders", len([o for o in kitchen_orders if o["status"] == "Order Placed"]))
    c2.metric("🔥 Active", len(active_orders))
    c3.metric("✅ Delivered Today", len(delivered_orders))
    c4.metric("💰 Revenue Today", f"₹{sum(o['grand_total'] for o in delivered_orders)}")
    
    st.divider()
    
    if not kitchen_orders:
        st.info("🍳 No orders yet for your kitchen today.")
    else:
        for order in reversed(kitchen_orders):
            if order["status"] == "Order Placed":
                bg_color = "#fef3c7"
                border_color = "#f59e0b"
            elif order["status"] in ["Accepted", "Preparing"]:
                bg_color = "#eff6ff"
                border_color = "#3b82f6"
            elif order["status"] == "Delivered":
                bg_color = "#f0fdf4"
                border_color = "#22c55e"
            else:
                bg_color = "#f9fafb"
                border_color = "#e5e7eb"
            
            with st.expander(f"📦 {order['id']} | {order['resident_name']} (Flat {order['flat']}) | {order['status']} | ₹{order['grand_total']}"):
                col_l, col_r = st.columns([2, 1])
                with col_l:
                    st.markdown("**Items Ordered:**")
                    for item in order["items"]:
                        st.write(f"  • {item['name']} ×{item['qty']}")
                    st.write(f"**📍 Delivery Flat:** {order['flat']}")
                    st.write(f"**⏰ Slot:** {order['slot']}")
                    if order.get("notes"):
                        st.info(f"📝 Notes: {order['notes']}")
                with col_r:
                    st.write(f"**Status:** {order['status']}")
                    if order["status"] not in ["Delivered", "Cancelled"]:
                        new_status = st.selectbox(
                            "Update to:",
                            STATUS_FLOW,
                            index=STATUS_FLOW.index(order["status"]) if order["status"] in STATUS_FLOW else 0,
                            key=f"k_status_{order['id']}"
                        )
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("✅ Update", key=f"kupd_{order['id']}", use_container_width=True):
                                for o in st.session_state.orders:
                                    if o["id"] == order["id"]:
                                        o["status"] = new_status
                                st.success(f"Updated to {new_status}")
                                st.rerun()
                        with col_btn2:
                            if st.button("❌ Cancel", key=f"kcancel_{order['id']}", use_container_width=True):
                                for o in st.session_state.orders:
                                    if o["id"] == order["id"]:
                                        o["status"] = "Cancelled"
                                st.rerun()

with tab2:
    st.markdown("### 📊 Kitchen Analytics")
    
    import pandas as pd
    kitchen_orders = [o for o in st.session_state.orders if o["kitchen_id"] == kitchen_id]
    
    if kitchen_orders:
        df = pd.DataFrame([{
            "Order ID": o["id"],
            "Resident": o["resident_name"],
            "Flat": o["flat"],
            "Amount": o["grand_total"],
            "Status": o["status"],
            "Slot": o["slot"]
        } for o in kitchen_orders])
        
        st.dataframe(df, use_container_width=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"))
        with col_b:
            st.metric("💰 Total Revenue", f"₹{df['Amount'].sum()}")
            st.metric("📊 Avg Order Value", f"₹{df['Amount'].mean():.0f}")
            st.metric("📦 Total Orders", len(df))
    else:
        st.info("No orders yet to analyze.")

with tab3:
    st.markdown("### 📖 My Menu")
    kitchen_meals = [m for m in data["meals"] if m["kitchen_id"] == kitchen_id]
    
    if not kitchen_meals:
        st.info("No meals found for your kitchen.")
    else:
        for meal in kitchen_meals:
            col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])
            with col1:
                st.write(meal["image"])
            with col2:
                veg = "🟢" if meal["veg"] else "🔴"
                st.write(f"{veg} **{meal['name']}** | {meal['category']}")
                st.caption(f"🌶️ {meal['spice']} | ⏱ {meal['prep_time']}min | ★ {meal['rating']}")
            with col3:
                st.write(f"₹{meal['price']}")
            with col4:
                avail = "✅" if meal["available"] else "❌"
                st.write(f"{avail} {'Available' if meal['available'] else 'Off'}")
            with col5:
                if st.button("✏️ Edit", key=f"edit_{meal['id']}"):
                    st.info(f"Edit mode for {meal['name']} (connect to backend to save)")

with tab4:
    st.markdown("### ⚙️ Kitchen Settings")
    col1, col2 = st.columns(2)
    with col1:
        new_status = st.selectbox("🟢 Kitchen Status", ["Open", "Closed", "On Break"], index=["Open", "Closed", "On Break"].index(kitchen["status"]) if kitchen["status"] in ["Open", "Closed", "On Break"] else 0)
        opening_time = st.text_input("Opening Time", kitchen["timing"].split("-")[0].strip())
        closing_time = st.text_input("Closing Time", kitchen["timing"].split("-")[1].strip() if "-" in kitchen["timing"] else "9PM")
    with col2:
        max_orders = st.number_input("📦 Max Simultaneous Orders", 1, 20, 5)
        prep_buffer = st.number_input("⏱ Extra Prep Buffer (min)", 0, 30, 5)
        st.checkbox("🔔 Enable order notifications", value=True)
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved! (Connect to backend to persist)")

with st.sidebar:
    st.markdown(f"## 👨‍🍳 {kitchen['name']}")
    st.caption(f"Owner: {kitchen['owner']}")
    kitchen_orders = [o for o in st.session_state.orders if o["kitchen_id"] == kitchen_id]
    new_count = len([o for o in kitchen_orders if o["status"] == "Order Placed"])
    if new_count > 0:
        st.warning(f"🔔 {new_count} new order(s) pending!")
    st.divider()
    st.page_link("pages/4_Order_Tracking.py", label="📦 All Orders")
    st.page_link("pages/7_Gate_Operations.py", label="🛡️ Gate Ops")
