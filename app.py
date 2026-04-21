import streamlit as st
import json
import os

# Page configuration
st.set_page_config(
    page_title="GateMeal",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load mock data
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "mock_data.json")
    with open(data_path, "r") as f:
        return json.load(f)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "cart" not in st.session_state:
    st.session_state.cart = []
if "role" not in st.session_state:
    st.session_state.role = None
if "orders" not in st.session_state:
    data = load_data()
    st.session_state.orders = data["orders"]
if "gate_logs" not in st.session_state:
    data = load_data()
    st.session_state.gate_logs = data["gate_logs"]

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-card {
        background: white;
        border: 2px solid #FF6B35;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
    }
    .role-card:hover {
        background: #FFF3EE;
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(255,107,53,0.2);
    }
    .status-delivered { color: #22c55e; font-weight: bold; }
    .status-preparing { color: #f59e0b; font-weight: bold; }
    .status-placed { color: #3b82f6; font-weight: bold; }
    .status-out { color: #8b5cf6; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    div[data-testid="stSidebarNav"] li div a span {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Main landing page
st.markdown("""
<div class="main-header">
    <h1>🍽️ GateMeal</h1>
    <p style="font-size:1.2rem; margin:0;">Your Community's Favourite Food Platform</p>
    <p style="font-size:0.9rem; opacity:0.85;">Fresh | Local | Delivered to Your Door</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.user is None:
    st.markdown("### 👋 Welcome to GateMeal!")
    st.markdown("Select your role to get started:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="role-card">
            <div style="font-size:3rem">🏠</div>
            <h3>Resident</h3>
            <p>Browse meals, order food, track delivery</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Enter as Resident", use_container_width=True, key="res_btn"):
            st.session_state.user = "Ganesh Gowri"
            st.session_state.role = "resident"
            st.session_state.resident_id = "R001"
            st.session_state.flat = "A-201"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="role-card">
            <div style="font-size:3rem">👨‍🍳</div>
            <h3>Kitchen Partner</h3>
            <p>Manage menu, accept & fulfill orders</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Enter as Kitchen", use_container_width=True, key="kit_btn"):
            st.session_state.user = "Amma's Kitchen"
            st.session_state.role = "kitchen"
            st.session_state.kitchen_id = "K001"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="role-card">
            <div style="font-size:3rem">🛡️</div>
            <h3>Gate / Security</h3>
            <p>Validate deliveries, manage access logs</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Enter as Gate", use_container_width=True, key="gate_btn"):
            st.session_state.user = "Security Officer"
            st.session_state.role = "gate"
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class="role-card">
            <div style="font-size:3rem">📊</div>
            <h3>Admin</h3>
            <p>Monitor operations, analytics, settings</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Enter as Admin", use_container_width=True, key="adm_btn"):
            st.session_state.user = "Admin"
            st.session_state.role = "admin"
            st.rerun()
    
    st.divider()
    st.markdown("### 📊 Platform Highlights")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍳 Kitchens", "4", "Active")
    c2.metric("🍝 Meals", "10+", "Available today")
    c3.metric("📦 Orders Today", "4", "Across community")
    c4.metric("★ Avg Rating", "4.6", "Community score")

else:
    role = st.session_state.role
    user = st.session_state.user
    
    st.markdown(f"### 👋 Welcome back, **{user}**! *(Role: {role.title()})*")
    
    if role == "resident":
        st.info("🏠 You are logged in as a **Resident**. Use the sidebar to browse meals, check your cart, or track orders.")
    elif role == "kitchen":
        st.info("👨‍🍳 You are logged in as a **Kitchen Partner**. Use the sidebar to manage your menu and incoming orders.")
    elif role == "gate":
        st.info("🛡️ You are logged in as **Gate Security**. Use the sidebar to manage deliveries and gate access logs.")
    elif role == "admin":
        st.info("📊 You are logged in as **Admin**. Full platform visibility and controls available in the sidebar.")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.cart = []
            st.rerun()
    
    # Quick navigation cards based on role
    st.divider()
    if role == "resident":
        st.markdown("#### ⚡ Quick Actions")
        q1, q2, q3 = st.columns(3)
        q1.page_link("pages/1_Resident_Home.py", label="🏠 My Dashboard", use_container_width=True)
        q2.page_link("pages/2_Browse_Meals.py", label="🔍 Browse & Order", use_container_width=True)
        q3.page_link("pages/4_Order_Tracking.py", label="📦 Track My Orders", use_container_width=True)
    elif role == "kitchen":
        q1, q2 = st.columns(2)
        q1.page_link("pages/5_Kitchen_Panel.py", label="👨‍🍳 Kitchen Panel", use_container_width=True)
        q2.page_link("pages/4_Order_Tracking.py", label="📦 All Orders", use_container_width=True)
    elif role == "gate":
        st.page_link("pages/7_Gate_Operations.py", label="🛡️ Gate Operations Panel", use_container_width=True)
    elif role == "admin":
        q1, q2 = st.columns(2)
        q1.page_link("pages/6_Admin_Dashboard.py", label="📊 Admin Dashboard", use_container_width=True)
        q2.page_link("pages/7_Gate_Operations.py", label="🛡️ Gate Logs", use_container_width=True)

# Sidebar info
with st.sidebar:
    st.markdown("## 🍽️ GateMeal")
    st.markdown("*Phase 1 - Community Food Platform*")
    if st.session_state.user:
        st.success(f"✅ {st.session_state.user}")
        st.caption(f"Role: {st.session_state.role.title()}")
    st.divider()
    st.markdown("**📍** Sunrise Residency, Vadlamudi")
    st.caption("© 2026 GateMeal Phase 1")
