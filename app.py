import streamlit as st
import uuid

# ✅ Rerun helper for newer Streamlit versions
try:
    from streamlit.runtime.scriptrunner import request_rerun
except ImportError:
    def request_rerun():
        st.warning("Please press enter key.")
        st.stop()

# ✅ Classes
class User:
    def __init__(self, name, role):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role

class Customer(User):
    def __init__(self, name):
        super().__init__(name, "Customer")

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Order:
    def __init__(self, customer):
        self.customer = customer
        self.items = []

    def add_item(self, item, qty):
        self.items.append((item, qty))

    def total(self):
        return sum(item.price * qty for item, qty in self.items)

class Table:
    def __init__(self, number):
        self.number = number
        self.is_booked = False
        self.order = None

    def reserve(self, customer):
        if self.is_booked:
            return False
        self.is_booked = True
        self.order = Order(customer)
        return True

    def release(self):
        self.is_booked = False
        self.order = None

# ✅ Menu items (static)
menu_items = [
    MenuItem("Pizza", 250),
    MenuItem("Burger", 150),
    MenuItem("Coke", 50),
    MenuItem("Pasta", 200),
    MenuItem("Salad", 100),
]

# ✅ Session state initialization
if "tables" not in st.session_state:
    st.session_state.tables = [Table(i) for i in range(1, 6)]

if "step" not in st.session_state:
    st.session_state.step = "get_name"

if "customer_name" not in st.session_state:
    st.session_state.customer_name = ""

if "reserved_table" not in st.session_state:
    st.session_state.reserved_table = None

if "order_quantities" not in st.session_state:
    st.session_state.order_quantities = {item.name: 0 for item in menu_items}

if "order_submitted" not in st.session_state:
    st.session_state.order_submitted = False

# ✅ Shortcut for tables
tables = st.session_state.tables

# ✅ App UI Start
st.title("🍽️ Restaurant Order System")

# Step 1: Get customer name
if st.session_state.step == "get_name":
    name = st.text_input("Enter your name:")
    if st.button("Next"):
        if name.strip() == "":
            st.warning("Please enter your name")
        else:
            st.session_state.customer_name = name.strip()
            st.session_state.step = "reserve_table"
            request_rerun()

# Step 2: Reserve Table
elif st.session_state.step == "reserve_table":
    available_tables = [t for t in tables if not t.is_booked]
    if not available_tables:
        st.error("No tables available")
    else:
        table_nums = [t.number for t in available_tables]
        table_selected = st.selectbox("Select Table to Reserve", table_nums)
        if st.button("Reserve Table"):
            table_obj = next(t for t in tables if t.number == table_selected)
            customer = Customer(st.session_state.customer_name)
            if table_obj.reserve(customer):
                st.session_state.reserved_table = table_obj.number
                st.session_state.step = "order_menu"
                request_rerun()
            else:
                st.error("Table already booked")

# Step 3: Show Menu and Take Order
elif st.session_state.step == "order_menu":
    st.write(f"🪑 Table {st.session_state.reserved_table} - Select quantities:")
    for item in menu_items:
        qty = st.number_input(
            f"{item.name} (₹{item.price})",
            min_value=0,
            max_value=20,
            value=st.session_state.order_quantities[item.name],
            key=item.name,
        )
        st.session_state.order_quantities[item.name] = qty

    if st.button("Submit Order"):
        if sum(st.session_state.order_quantities.values()) == 0:
            st.warning("Please select at least one item")
        else:
            table_obj = next(t for t in tables if t.number == st.session_state.reserved_table)
            if table_obj.order is None:
                customer = Customer(st.session_state.customer_name)
                table_obj.order = Order(customer)
            else:
                table_obj.order.items.clear()

            for item in menu_items:
                qty = st.session_state.order_quantities[item.name]
                if qty > 0:
                    table_obj.order.add_item(item, qty)

            st.session_state.order_submitted = True
            st.session_state.step = "show_bill"
            request_rerun()

# Step 4: Show Bill
elif st.session_state.step == "show_bill":
    table_obj = next(t for t in tables if t.number == st.session_state.reserved_table)
    st.subheader("🧾 Your Bill")
    total = 0
    for item, qty in table_obj.order.items:
        cost = item.price * qty
        total += cost
        st.write(f"{item.name} x {qty} = ₹{cost}")
    st.markdown(f"**Total: ₹{total}**")

    if st.button("Release Table"):
        table_obj.release()
        st.session_state.clear()
        request_rerun()

    if st.button("New Order"):
        st.session_state.clear()
        st.session_state.step = "get_name"
        request_rerun()
