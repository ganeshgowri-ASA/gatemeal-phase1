import streamlit as st
import json
import os
import random
import string
from datetime import datetime

st.set_page_config(page_title="Cart & Checkout - GateMeal", page_icon="🛒", layout="wide")

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

if "orders" not in st.session_state:
    st.session_state.orders = data["orders"]

st.markdown("""
<div style='background:linear-gradient(135deg,#059669,#10b981);padding:1.5rem;border-radius:12px;color:white;margin-bottom:1.5rem;'>
    <h2>🛒 Cart & Checkout</h2>
    <p style='margin:0;'>Review your items and place your order</p>
</div>
""", unsafe_allow_html=True)

cart = st.session_state.cart

if not cart:
    st.info("📦 Your cart is empty! Browse meals to add items.")
    st.page_link("pages/2_Browse_Meals.py", label="🔍 Browse Meals")
else:
    col_main, col_summary = st.columns([2, 1])

    with col_main:
        st.markdown("### 🛒 Your Cart Items")
        
        updated_cart = []
        for i, item in enumerate(cart):
            col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
            with col_a:
                veg_icon = "🟢" 
                st.write(f"{veg_icon} **{item['name']}** | {item.get('kitchen_name', '')}")
            with col_b:
                new_qty = st.number_input("", min_value=0, max_value=10, value=item["qty"], key=f"cart_qty_{i}")
            with col_c:
                st.write(f"₹{item['price'] * new_qty}")
            with col_d:
                if st.button("🗑️", key=f"del_{i}"):
                    continue
            if new_qty > 0:
                item["qty"] = new_qty
                updated_cart.append(item)
        
        st.session_state.cart = updated_cart
        
        if st.button("🧹 Clear All", type="secondary"):
            st.session_state.cart = []
            st.rerun()

    with col_summary:
        st.markdown("### 📋 Order Summary")
        
        subtotal = sum(i["price"] * i["qty"] for i in cart)
        delivery_fee = 20
        convenience_fee = 5
        total = subtotal + delivery_fee + convenience_fee
        
        st.markdown(f"""
        <div style='background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:1.2rem;'>
            <table width='100%'>
                <tr><td>Subtotal</td><td align='right'>₹{subtotal}</td></tr>
                <tr><td>Delivery Fee</td><td align='right'>₹{delivery_fee}</td></tr>
                <tr><td>Convenience Fee</td><td align='right'>₹{convenience_fee}</td></tr>
                <tr style='font-weight:bold;font-size:1.1rem;border-top:1px solid #e5e7eb;'>
                    <td style='padding-top:0.5rem;'>Total</td>
                    <td align='right' style='color:#FF6B35;padding-top:0.5rem;'>₹{total}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("#### 📍 Delivery Details")
        
        resident_name = getattr(st.session_state, "user", "Resident")
        flat = st.session_state.get("flat", "A-201")
        
        delivery_slot = st.selectbox("⏰ Delivery Slot", ["8:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "7:00 PM", "8:00 PM"])
        notes = st.text_area("📝 Notes to Kitchen", placeholder="e.g. Less spice, no onion...", height=80)
        
        st.markdown("#### 💳 Payment Method")
        payment = st.radio("", ["UPI", "Card (saved)", "Cash on Delivery"], label_visibility="collapsed")
        
        st.divider()
        
        if st.button("✅ Place Order", type="primary", use_container_width=True):
            # Generate order
            otp = ''.join(random.choices(string.digits, k=4))
            order_id = f"ORD{str(len(st.session_state.orders)+1).zfill(3)}"
            kitchen_id = cart[0]["kitchen_id"]
            kitchen_name = cart[0].get("kitchen_name", "Kitchen")
            
            new_order = {
                "id": order_id,
                "resident_id": st.session_state.get("resident_id", "R001"),
                "resident_name": resident_name,
                "flat": flat,
                "kitchen_id": kitchen_id,
                "kitchen_name": kitchen_name,
                "items": [{"meal_id": i["meal_id"], "name": i["name"], "qty": i["qty"], "price": i["price"]} for i in cart],
                "total": subtotal,
                "delivery_fee": delivery_fee + convenience_fee,
                "grand_total": total,
                "status": "Order Placed",
                "slot": delivery_slot,
                "placed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "delivered_at": None,
                "gate_entry": "Pending",
                "runner": None,
                "otp": otp,
                "rating": None,
                "notes": notes,
                "payment": payment
            }
            
            st.session_state.orders.append(new_order)
            st.session_state.cart = []
            
            st.success(f"✅ Order **{order_id}** placed successfully!")
            st.balloons()
            st.markdown(f"""
            <div style='background:#ecfdf5;border:2px solid #22c55e;border-radius:10px;padding:1.2rem;margin-top:1rem;'>
                <h3 style='color:#15803d;'>🎉 Order Confirmed!</h3>
                <p><strong>Order ID:</strong> {order_id}</p>
                <p><strong>OTP for Delivery:</strong> <span style='font-size:1.5rem;font-weight:bold;color:#FF6B35;'>{otp}</span></p>
                <p><strong>Slot:</strong> {delivery_slot}</p>
                <p><strong>Payment:</strong> {payment}</p>
                <p style='color:#6b7280;font-size:0.85rem;'>Share this OTP with the delivery runner to confirm receipt.</p>
            </div>
            """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🛒 Cart")
    cart = st.session_state.get("cart", [])
    if cart:
        total_items = sum(c["qty"] for c in cart)
        st.info(f"{total_items} item(s) in cart")
    else:
        st.caption("Cart is empty")
    st.divider()
    st.page_link("pages/2_Browse_Meals.py", label="🔍 Browse More Meals")
    st.page_link("pages/4_Order_Tracking.py", label="📦 Track My Orders")
