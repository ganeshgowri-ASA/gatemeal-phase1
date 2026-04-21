import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gate Operations - GateMeal", page_icon="🛡️", layout="wide")

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

if st.session_state.role not in ["gate", "admin"]:
    st.error("🚫 Access denied. Gate Security or Admin only.")
    st.stop()

if "orders" not in st.session_state:
    st.session_state.orders = data["orders"]

if "gate_logs" not in st.session_state:
    st.session_state.gate_logs = data["gate_logs"]

st.markdown("""
<div style='background:linear-gradient(135deg,#064e3b,#065f46);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>🛡️ Gate Operations Panel</h2>
    <p style='margin:0;'>Delivery access control, validation, and gate entry logs</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚚 Incoming Deliveries", "📝 Gate Logs", "🔐 OTP Verification"])

with tab1:
    st.markdown("### 🚚 Incoming Deliveries")
    
    orders = st.session_state.orders
    out_for_delivery = [o for o in orders if o["status"] == "Out for Delivery"]
    pending_gate = [o for o in orders if o["gate_entry"] == "Pending" and o["status"] not in ["Delivered", "Cancelled", "Order Placed"]]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚚 Out for Delivery", len(out_for_delivery))
    c2.metric("⏳ Gate Pending", len(pending_gate))
    c3.metric("✅ Gate Confirmed", len([o for o in orders if o.get("gate_entry") == "Confirmed"]))
    c4.metric("📍 Active Inside", len([g for g in st.session_state.gate_logs if g["status"] == "Inside"]))
    
    st.divider()
    
    if not pending_gate and not out_for_delivery:
        st.success("✅ No pending deliveries at gate right now.")
    
    all_active = list({o["id"]: o for o in (pending_gate + out_for_delivery)}.values())
    
    for order in all_active:
        gate_status = order.get("gate_entry", "Pending")
        if gate_status == "Confirmed":
            border = "#22c55e"
        elif gate_status == "Pending":
            border = "#f59e0b"
        else:
            border = "#e5e7eb"
        
        with st.expander(f"📦 {order['id']} | 🚚 {order.get('runner', 'TBD')} | 🏠 Flat {order['flat']} | Kitchen: {order['kitchen_name']} | Gate: {gate_status}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**📦 Order:** {order['id']}")
                st.write(f"**🏠 Resident:** {order['resident_name']}")
                st.write(f"**📍 Flat:** {order['flat']}")
                st.write(f"**🍳 Kitchen:** {order['kitchen_name']}")
            with col2:
                st.write(f"**🚚 Runner:** {order.get('runner') or 'Assigning...'}")
                st.write(f"**⏰ Slot:** {order['slot']}")
                st.write(f"**💰 Amount:** ₹{order['grand_total']}")
                st.write(f"**🗡️ Status:** {order['status']}")
            with col3:
                st.markdown(f"**OTP:** <span style='font-size:1.5rem;font-weight:bold;color:#FF6B35;'>{order.get('otp', '----')}</span>", unsafe_allow_html=True)
                
                if gate_status != "Confirmed":
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅ Confirm Entry", key=f"gate_confirm_{order['id']}", use_container_width=True):
                            for o in st.session_state.orders:
                                if o["id"] == order["id"]:
                                    o["gate_entry"] = "Confirmed"
                            # Add gate log
                            new_log = {
                                "id": f"G{len(st.session_state.gate_logs)+1:03d}",
                                "order_id": order["id"],
                                "agent": order.get("runner", "Unknown"),
                                "kitchen": order["kitchen_name"],
                                "flat": order["flat"],
                                "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "exit_time": None,
                                "status": "Inside"
                            }
                            st.session_state.gate_logs.append(new_log)
                            st.success(f"✅ Entry confirmed for {order['id']}")
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ Deny", key=f"gate_deny_{order['id']}", use_container_width=True):
                            for o in st.session_state.orders:
                                if o["id"] == order["id"]:
                                    o["gate_entry"] = "Denied"
                            st.warning(f"⚠️ Entry denied for {order['id']}")
                            st.rerun()
                else:
                    st.success("✅ Entry Confirmed")
                    if st.button("🛣️ Mark Exit", key=f"gate_exit_{order['id']}"):
                        for log in st.session_state.gate_logs:
                            if log["order_id"] == order["id"] and log["status"] == "Inside":
                                log["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                log["status"] = "Completed"
                        st.rerun()

with tab2:
    st.markdown("### 📝 Gate Entry Logs")
    
    logs = st.session_state.gate_logs
    
    if logs:
        df_logs = pd.DataFrame([{
            "Log ID": g["id"],
            "Order ID": g["order_id"],
            "Agent/Runner": g["agent"],
            "Kitchen": g["kitchen"],
            "Flat": g["flat"],
            "Entry Time": g["entry_time"],
            "Exit Time": g.get("exit_time") or "Still Inside",
            "Status": g["status"]
        } for g in logs])
        
        st.dataframe(df_logs, use_container_width=True)
        
        inside_count = len([g for g in logs if g["status"] == "Inside"])
        if inside_count > 0:
            st.warning(f"🚨 {inside_count} delivery agent(s) currently inside the community")
        else:
            st.success("✅ No delivery agents currently inside")
    else:
        st.info("No gate logs recorded yet.")

with tab3:
    st.markdown("### 🔐 OTP Verification")
    st.info("🔐 Use this to manually verify an OTP if a resident wants to confirm delivery at the gate.")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        order_id_input = st.text_input("📦 Enter Order ID", placeholder="e.g. ORD001")
    with col_v2:
        otp_input = st.text_input("🔐 Enter OTP", placeholder="4-digit OTP", max_chars=4)
    
    if st.button("✅ Verify OTP", type="primary"):
        if order_id_input and otp_input:
            matched = next((o for o in st.session_state.orders if o["id"].upper() == order_id_input.upper() and o["otp"] == otp_input), None)
            if matched:
                st.success(f"✅ OTP Verified! Order **{matched['id']}** for **{matched['resident_name']}** (Flat {matched['flat']}) - ₹{matched['grand_total']}")
                st.balloons()
                # Mark as delivered
                if matched["status"] == "Out for Delivery":
                    if st.button("🎉 Mark as Delivered", type="primary"):
                        for o in st.session_state.orders:
                            if o["id"] == matched["id"]:
                                o["status"] = "Delivered"
                                o["delivered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.success("✅ Order marked as delivered!")
                        st.rerun()
            else:
                st.error("❌ Invalid OTP or Order ID. Please check and try again.")
        else:
            st.warning("Please enter both Order ID and OTP.")

with st.sidebar:
    st.markdown("## 🛡️ Gate Panel")
    st.caption(f"Officer: {st.session_state.user}")
    logs = st.session_state.gate_logs
    inside = len([g for g in logs if g["status"] == "Inside"])
    if inside > 0:
        st.warning(f"🚚 {inside} agent(s) inside")
    else:
        st.success("✅ Community clear")
    st.divider()
    pending = len([o for o in st.session_state.orders if o["gate_entry"] == "Pending" and o["status"] not in ["Delivered", "Cancelled", "Order Placed"]])
    if pending > 0:
        st.error(f"⏳ {pending} pending at gate")
    st.divider()
    st.page_link("pages/4_Order_Tracking.py", label="📦 All Orders")
    if st.session_state.role == "admin":
        st.page_link("pages/6_Admin_Dashboard.py", label="📊 Admin")
