# 🍽️ GateMeal Phase 1

> **A gated-community meal ordering and delivery management platform built with Streamlit.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gatemeal-phase1.streamlit.app)

---

## 📌 Overview

GateMeal is a Phase 1 prototype for a community-driven food ordering platform designed for **gated residential communities**. It connects residents, home chefs/kitchens, delivery agents, gate security, and admins into a single, seamless ecosystem.

**Community:** Sunrise Residency, Vadlamudi, Andhra Pradesh

---

## 🌟 Features

### 🏠 Resident App
- Login simulation with flat & dietary profile
- Featured kitchen discovery
- Browse & filter meals (category, diet, price, spice, kitchen)
- Add to cart with quantity selection
- Checkout with slot selection, notes, payment method
- OTP-secured order confirmation
- Live order status tracking with timeline
- Recent order history

### 👨‍🍳 Kitchen Partner Panel
- Incoming orders queue with real-time status control
- Accept / update status (Accepted → Preparing → Ready)
- Cancel orders
- Revenue analytics with charts
- Menu management view
- Kitchen settings (status, timing, capacity)

### 📦 Order Tracking (Multi-role)
- Real-time 6-step order lifecycle tracking
- Timeline visualization per order
- Kitchen & admin can update order status
- Search by Order ID or Flat number
- Status filter

### 📊 Admin Dashboard
- Platform KPIs (GMV, orders, delivery rate)
- Full order table with filters and CSV export
- Kitchen management view
- Resident directory
- Delivery agent roster
- Analytics charts (status distribution, revenue by kitchen)

### 🛡️ Gate Operations Panel
- Live incoming delivery queue
- Confirm/deny gate entry
- Mark delivery agent exit
- Gate entry/exit audit log
- OTP verification terminal
- Mark order as Delivered after OTP confirmation

---

## 📁 Project Structure

```
gatemeal-phase1/
├── app.py                      # Main entry point (role selector + home)
├── requirements.txt
├── README.md
├── data/
│   └── mock_data.json          # Seed data (kitchens, meals, orders, residents, agents, gate logs)
└── pages/
    ├── 1_Resident_Home.py      # Resident dashboard + meal discovery
    ├── 2_Browse_Meals.py       # Full meal catalog with filters
    ├── 3_Cart_Checkout.py      # Cart management + order placement + OTP
    ├── 4_Order_Tracking.py     # Live order status tracker (all roles)
    ├── 5_Kitchen_Panel.py      # Kitchen orders + analytics + menu + settings
    ├── 6_Admin_Dashboard.py    # Platform-wide admin view + analytics
    └── 7_Gate_Operations.py    # Gate entry/exit control + OTP verification
```

---

## 📊 Mock Data Included

- **4 Kitchens:** Amma's Kitchen (South Indian), Punjabi Tadka (North Indian), Healthy Bites, Dragon Wok
- **10 Meals** across Breakfast, Lunch, Dinner, Snacks
- **3 Residents:** Ganesh Gowri (A-201), Anita Reddy (B-302), Ravi Kumar (C-101)
- **4 Sample Orders** in various states (Delivered, Out for Delivery, Preparing, Placed)
- **3 Delivery Agents:** Ramu, Suresh, Venkat
- **2 Gate Logs** with entry/exit records

---

## 🚀 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/ganeshgowri-ASA/gatemeal-phase1.git
cd gatemeal-phase1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select repository: `ganeshgowri-ASA/gatemeal-phase1`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **Deploy**

---

## 📱 User Roles & Demo Logins

| Role | Access | Demo User |
|------|--------|----------|
| 🏠 Resident | Browse, Order, Track | Ganesh Gowri (Flat A-201) |
| 👨‍🍳 Kitchen | Manage orders, menu | Amma's Kitchen |
| 🛡️ Gate Security | Delivery validation | Security Officer |
| 📊 Admin | Full platform view | Admin |

---

## 🛣️ Phase 2 Roadmap

- [ ] Backend API (FastAPI/Django)
- [ ] Real database (PostgreSQL/MongoDB)
- [ ] Mobile-responsive PWA
- [ ] Push notifications
- [ ] Meal subscription & recurring orders
- [ ] Group orders for families
- [ ] Resident wallet & loyalty points
- [ ] AI meal recommendations
- [ ] Vendor performance scoring
- [ ] Multi-community support

---

## 📍 Built For

**Sunrise Residency, Vadlamudi, Andhra Pradesh, IN**

Built with ❤️ using Python + Streamlit | GateMeal Phase 1 © 2026
