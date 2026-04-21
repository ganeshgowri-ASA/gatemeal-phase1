import streamlit as st
import json
import os

st.set_page_config(page_title="Order Tracking - GateMeal", page_icon="📦", layout="wide")

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

if "orders" not in st.session_state:
    st.session_state.orders = data["orders"]

st.markdown("""
<div style='background:linear-gradient(135deg,#0ea5e9,#0284c7);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>📦 Order Tracking</h2>
    <p style='margin:0;'>Live status of all orders across the community</p>
</div>
""", unsafe_allow_html=True)

STATUS_FLOW = ["Order Placed", "Accepted", "Preparing", "Ready for Pickup", "Out for Delivery", "Delivered"]

STATUS_COLORS = {
    "Order Placed": "#3b82f6",
    "Accepted": "#8b5cf6",
    "Preparing": "#f59e0b",
    "Ready for Pickup": "#f97316",
    "Out for Delivery": "#a855f7",
    "Delivered": "#22c55e",
    "Cancelled": "#ef4444"
}

STATUS_ICONS = {
    "Order Placed": "🔵",
    "Accepted": "🟣",
    "Preparing": "🟡",
    "Ready for Pickup": "🟠",
    "Out for Delivery": "🚨",
    "Delivered": "🟢",
    "Cancelled": "⚫"
}

role = st.session_state.role
orders = st.session_state.orders

# Filter by role
if role == "resident":
    resident_id = st.session_state.get("resident_id", "R001")
    display_orders = [o for o in orders if o["resident_id"] == resident_id]
elif role == "kitchen":
    kitchen_id = st.session_state.get("kitchen_id", "K001")
    display_orders = [o for o in orders if o["kitchen_id"] == kitchen_id]
else:
    display_orders = orders

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total", len(display_orders))
col2.metric("⏳ Active", len([o for o in display_orders if o["status"] not in ["Delivered", "Cancelled"]]))
col3.metric("🚚 Out for Delivery", len([o for o in display_orders if o["status"] == "Out for Delivery"]))
col4.metric("✅ Delivered", len([o for o in display_orders if o["status"] == "Delivered"]))

st.divider()

# Filters
col_f1, col_f2 = st.columns(2)
with col_f1:
    status_filter = st.selectbox("📊 Filter by Status", ["All"] + STATUS_FLOW + ["Cancelled"])
with col_f2:
    search_order = st.text_input("🔎 Search Order ID or Flat", placeholder="ORD001 or A-201")

if status_filter != "All":
    display_orders = [o for o in display_orders if o["status"] == status_filter]
if search_order:
    display_orders = [o for o in display_orders if search_order.upper() in o["id"].upper() or search_order in o["flat"]]

if not display_orders:
    st.info("📦 No orders found.")
else:
    for order in reversed(display_orders):
        status = order["status"]
        color = STATUS_COLORS.get(status, "#6b7280")
        icon = STATUS_ICONS.get(status, "⚪")
        
        with st.expander(f"{icon} **{order['id']}** | {order['resident_name']} ({order['flat']}) | {order['kitchen_name']} | ₹{order['grand_total']} | **{status}**", expanded=(status not in ["Delivered"])):
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.markdown("**🗡️ Order Items:**")
                for item in order["items"]:
                    st.write(f"  • {item['name']} x{item['qty']} = ₹{item['price']*item['qty']}")
                st.write(f"**💰 Grand Total:** ₹{order['grand_total']}")
                st.write(f"**⏰ Slot:** {order['slot']} | **Placed:** {order['placed_at']}")
                if order.get('delivered_at'):
                    st.write(f"**✅ Delivered at:** {order['delivered_at']}")
                st.write(f"**🚚 Runner:** {order.get('runner') or 'Not assigned yet'}")
                st.write(f"**🛡️ Gate Entry:** {order.get('gate_entry', 'Pending')}")
            
            with col_right:
                st.markdown("**📍 Order Timeline**")
                for step in STATUS_FLOW:
                    try:
                        step_idx = STATUS_FLOW.index(step)
                        curr_idx = STATUS_FLOW.index(status) if status in STATUS_FLOW else -1
                        if step_idx < curr_idx:
                            st.markdown(f"✅ ~~{step}~~")
                        elif step_idx == curr_idx:
                            st.markdown(f"**🟡 {step} (Current)**")
                        else:
                            st.markdown(f"⏳ {step}")
                    except:
                        pass
                
                st.divider()
                st.markdown(f"**OTP:** `{order.get('otp', '----')}`")
                
                # Status update (for kitchen/admin)
                if role in ["kitchen", "admin"]:
                    new_status = st.selectbox("Update Status", STATUS_FLOW, index=STATUS_FLOW.index(status) if status in STATUS_FLOW else 0, key=f"status_{order['id']}")
                    if st.button("Update", key=f"upd_{order['id']}"):
                        for o in st.session_state.orders:
                            if o["id"] == order["id"]:
                                o["status"] = new_status
                                if new_status == "Out for Delivery" and not o.get("runner"):
                                    o["runner"] = "Ramu"
                        st.success(f"Status updated to: {new_status}")
                        st.rerun()

with st.sidebar:
    st.markdown("## 📦 Order Tracking")
    st.caption(f"Logged in as: {st.session_state.role.title()}")
    active_count = len([o for o in st.session_state.orders if o["status"] not in ["Delivered", "Cancelled"]])
    if active_count > 0:
        st.warning(f"⏳ {active_count} active order(s)")
    else:
        st.success("✅ All orders delivered")
    st.divider()
    if role == "resident":
        st.page_link("pages/2_Browse_Meals.py", label="🔍 Order More Food")
    elif role in ["kitchen", "admin"]:
        st.page_link("pages/5_Kitchen_Panel.py", label="🍳 Kitchen Panel")
        st.page_link("pages/7_Gate_Operations.py", label="🛡️ Gate Ops")
