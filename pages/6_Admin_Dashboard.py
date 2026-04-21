import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="Admin Dashboard - GateMeal", page_icon="📊", layout="wide")

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

if st.session_state.role != "admin":
    st.error("🚫 Access denied. Admin only.")
    st.stop()

if "orders" not in st.session_state:
    st.session_state.orders = data["orders"]

st.markdown("""
<div style='background:linear-gradient(135deg,#1e1b4b,#312e81);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>📊 GateMeal Admin Dashboard</h2>
    <p style='margin:0;'>Full platform oversight - Orders, Kitchens, Residents, Analytics</p>
</div>
""", unsafe_allow_html=True)

orders = st.session_state.orders

# Top KPIs
st.markdown("### 🎯 Platform KPIs")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("📦 Total Orders", len(orders))
k2.metric("✅ Delivered", len([o for o in orders if o["status"] == "Delivered"]))
k3.metric("⏳ Active", len([o for o in orders if o["status"] not in ["Delivered", "Cancelled"]]))
k4.metric("🍳 Kitchens", len(data["kitchens"]))
k5.metric("🏠 Residents", len(data["residents"]))
k6.metric("💰 GMV Today", f"₹{sum(o['grand_total'] for o in orders)}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Orders", "🍳 Kitchens", "🏠 Residents", "🚚 Delivery Agents", "📈 Analytics"])

with tab1:
    st.markdown("### 📦 All Orders")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        status_filter = st.selectbox("Filter by Status", ["All", "Order Placed", "Accepted", "Preparing", "Ready for Pickup", "Out for Delivery", "Delivered", "Cancelled"])
    with col_f2:
        kitchen_filter = st.selectbox("Filter by Kitchen", ["All"] + [k["name"] for k in data["kitchens"]])
    
    filtered = orders
    if status_filter != "All":
        filtered = [o for o in filtered if o["status"] == status_filter]
    if kitchen_filter != "All":
        filtered = [o for o in filtered if o["kitchen_name"] == kitchen_filter]
    
    if filtered:
        df_orders = pd.DataFrame([{
            "Order ID": o["id"],
            "Resident": o["resident_name"],
            "Flat": o["flat"],
            "Kitchen": o["kitchen_name"],
            "Amount": f"₹{o['grand_total']}",
            "Status": o["status"],
            "Slot": o["slot"],
            "Gate": o.get("gate_entry", "Pending"),
            "OTP": o.get("otp", "---")
        } for o in filtered])
        st.dataframe(df_orders, use_container_width=True)
    else:
        st.info("No orders match filters.")
    
    # Bulk status update
    st.divider()
    st.markdown("**Quick Actions**")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔄 Refresh Orders"):
            st.rerun()
    with col_b:
        if st.button("📊 Export CSV"):
            if filtered:
                csv_df = pd.DataFrame([{
                    "Order ID": o["id"], "Resident": o["resident_name"],
                    "Kitchen": o["kitchen_name"], "Amount": o["grand_total"],
                    "Status": o["status"]
                } for o in filtered])
                st.download_button("Download CSV", csv_df.to_csv(index=False), "orders.csv", "text/csv")

with tab2:
    st.markdown("### 🍳 Kitchen Management")
    for kitchen in data["kitchens"]:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
        with col1:
            st.write(f"**{kitchen['name']}** | {kitchen['owner']}")
            st.caption(f"{kitchen['cuisine']} | {kitchen['timing']}")
        with col2:
            veg = "🌱 Veg Only" if kitchen["veg_only"] else "🍖 Mixed"
            st.write(f"★ {kitchen['rating']} | {kitchen['reviews']} reviews")
            st.caption(f"{veg} | Block {kitchen['block']}, {kitchen['flat']}")
        with col3:
            status_color = "#22c55e" if kitchen["status"] == "Open" else "#ef4444"
            st.markdown(f"<span style='color:{status_color};font-weight:bold;'>{kitchen['status']}</span>", unsafe_allow_html=True)
        with col4:
            k_orders = len([o for o in orders if o["kitchen_id"] == kitchen["id"]])
            st.metric("📦", k_orders)
        with col5:
            if st.button("✏️", key=f"kedit_{kitchen['id']}"):
                st.info(f"Editing {kitchen['name']} - connect to backend")
        st.divider()

with tab3:
    st.markdown("### 🏠 Residents")
    df_res = pd.DataFrame([{
        "ID": r["id"],
        "Name": r["name"],
        "Flat": r["flat"],
        "Block": r["block"],
        "Tower": r["tower"],
        "Phone": r["phone"],
        "Diet": r["dietary"]
    } for r in data["residents"]])
    st.dataframe(df_res, use_container_width=True)
    st.caption(f"Total registered residents: {len(data['residents'])}")

with tab4:
    st.markdown("### 🚚 Delivery Agents")
    for agent in data["delivery_agents"]:
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            st.write(f"**{agent['name']}** | {agent['phone']}")
        with col2:
            status_icon = "🟢" if agent["status"] == "Available" else "🟡"
            st.write(f"{status_icon} {agent['status']}")
        with col3:
            if agent.get("current_order"):
                st.write(f"📦 Delivering: {agent['current_order']}")
            else:
                st.write("✅ Free")
        st.divider()

with tab5:
    st.markdown("### 📈 Analytics")
    
    if orders:
        df_all = pd.DataFrame([{
            "Kitchen": o["kitchen_name"],
            "Status": o["status"],
            "Amount": o["grand_total"],
            "Slot": o["slot"]
        } for o in orders])
        
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Orders by Status**")
            status_data = df_all["Status"].value_counts().reset_index()
            status_data.columns = ["Status", "Count"]
            st.bar_chart(status_data.set_index("Status"))
        with col_r:
            st.markdown("**Revenue by Kitchen**")
            rev_data = df_all.groupby("Kitchen")["Amount"].sum().reset_index()
            st.bar_chart(rev_data.set_index("Kitchen"))
        
        st.divider()
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("💰 Total GMV", f"₹{df_all['Amount'].sum()}")
        col_m2.metric("📊 Avg Order Value", f"₹{df_all['Amount'].mean():.0f}")
        col_m3.metric("✅ Delivery Rate", f"{len(df_all[df_all['Status']=='Delivered'])/len(df_all)*100:.0f}%")
    else:
        st.info("No analytics data yet.")

with st.sidebar:
    st.markdown("## 📊 Admin Panel")
    st.success("👍 Admin Access")
    st.divider()
    active_count = len([o for o in orders if o["status"] not in ["Delivered", "Cancelled"]])
    if active_count > 0:
        st.warning(f"⏳ {active_count} active orders")
    st.divider()
    st.page_link("pages/4_Order_Tracking.py", label="📦 Order Tracking")
    st.page_link("pages/5_Kitchen_Panel.py", label="🍳 Kitchen Panel")
    st.page_link("pages/7_Gate_Operations.py", label="🛡️ Gate Operations")
