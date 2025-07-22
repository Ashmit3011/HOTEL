import streamlit as st
import json
import os
import time
from datetime import datetime

# -------------------- Config & Styling --------------------
st.set_page_config(page_title="Smart Table Order", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        #MainMenu, footer {visibility: hidden;}
        .stButton > button {
            padding: 0.3rem 0.6rem !important;
            font-size: 0.8rem !important;
        }
        .status-bar {
            height: 8px;
            border-radius: 5px;
            margin-top: 8px;
            background: linear-gradient(to right, orange 33%, gray 33%);
        }
        .progress-pending { background: linear-gradient(to right, orange 33%, lightgray 33%); }
        .progress-preparing { background: linear-gradient(to right, #03a9f4 66%, lightgray 66%); }
        .progress-completed { background: linear-gradient(to right, #4caf50 100%, #4caf50 100%); }
        .toast {
            padding: 10px;
            background-color: #323232;
            color: white;
            border-radius: 5px;
            animation: fadein 0.5s;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- Paths --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# -------------------- Load Menu --------------------
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error("❌ Menu file not found!")
    st.stop()

# -------------------- Load Orders --------------------
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# -------------------- Ask for Table --------------------
if "table_number" not in st.session_state or not st.session_state.table_number:
    st.title("🍽️ Smart Table Ordering System")
    table_number = st.text_input("🔢 Enter your Table Number")
    if table_number:
        st.session_state.table_number = table_number
        st.session_state.cart = {}
        st.session_state.last_status = None
        st.rerun()
    st.stop()

st.title(f"🍽️ Smart Table Ordering — Table {st.session_state.table_number}")

# -------------------- Init Cart --------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}

# -------------------- Show Menu --------------------
st.subheader("📋 Menu")
for category, items in menu.items():
    with st.expander(category):
        for item in items:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{item['name']}** — ₹{item['price']}")
            with col2:
                if st.button("➕", key=f"{category}-{item['name']}"):
                    name, price = item["name"], item["price"]
                    if name not in st.session_state.cart:
                        st.session_state.cart[name] = {"price": price, "quantity": 1}
                    else:
                        st.session_state.cart[name]["quantity"] += 1
                    st.rerun()

# -------------------- Show Cart --------------------
st.subheader("🛒 Cart")
if st.session_state.cart:
    total = 0
    for name, item in list(st.session_state.cart.items()):
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        with st.container():
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                st.markdown(f"**{name}** x {item['quantity']} = ₹{subtotal}")
            with col2:
                if st.button("➖", key=f"decrease-{name}"):
                    item["quantity"] -= 1
                    if item["quantity"] <= 0:
                        del st.session_state.cart[name]
                    st.rerun()
            with col3:
                if st.button("❌", key=f"remove-{name}"):
                    del st.session_state.cart[name]
                    st.rerun()

    st.markdown(f"### 🧾 Total: ₹{total}")
    if st.button("✅ Place Order"):
        orders = [o for o in orders if o["table"] != st.session_state.table_number]
        new_order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)
        st.success("✅ Order Placed!")
        del st.session_state.cart
        st.session_state.last_status = "Pending"
        st.rerun()
else:
    st.info("🛍️ Your cart is empty.")

# -------------------- Track Orders --------------------
st.subheader("📦 Your Orders")
found = False
for order in reversed(orders):
    if order["table"] == st.session_state.table_number:
        found = True
        status = order["status"]

        # 🔔 Sound alert if status changes to Preparing
        if "last_status" in st.session_state and st.session_state.last_status != status:
            if status == "Preparing":
                st.audio("https://www.soundjay.com/buttons/sounds/button-10.mp3", autoplay=True)
                st.markdown(f"<div class='toast'>👨‍🍳 Your order is now being prepared!</div>", unsafe_allow_html=True)
            elif status == "Completed":
                st.markdown(f"<div class='toast'>✅ Your order is completed!</div>", unsafe_allow_html=True)
            elif status == "Cancelled":
                st.markdown(f"<div class='toast'>❌ Your order was cancelled!</div>", unsafe_allow_html=True)
            st.session_state.last_status = status

        st.markdown(f"""
            <div style="margin-bottom: 0.3rem;">
                <strong>Status:</strong> <span style="color: #009688;">{status}</span><br>
                <small>{order['timestamp']}</small>
            </div>
        """, unsafe_allow_html=True)

        # Animated status bar
        if status == "Pending":
            st.markdown('<div class="status-bar progress-pending"></div>', unsafe_allow_html=True)
        elif status == "Preparing":
            st.markdown('<div class="status-bar progress-preparing"></div>', unsafe_allow_html=True)
        elif status == "Completed":
            st.markdown('<div class="status-bar progress-completed"></div>', unsafe_allow_html=True)

        for name, item in order["items"].items():
            line = f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}"
            st.markdown(line if status != "Cancelled" else f"<s>{line}</s>", unsafe_allow_html=True)

        if status not in ["Completed", "Cancelled"]:
            if st.button(f"❌ Cancel Order ({order['timestamp']})", key=order["timestamp"]):
                order["status"] = "Cancelled"
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.warning("Order cancelled.")
                st.rerun()
        st.markdown("---")

if not found:
    st.info("📭 No orders found.")

# -------------------- Auto-Refresh --------------------
with st.empty():
    time.sleep(10)
    st.rerun()
