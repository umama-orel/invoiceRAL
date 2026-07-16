import streamlit as st
from datetime import datetime
from fpdf import FPDF
import os

# Set page configuration
st.set_page_config(page_title="Radiant Alliance - Invoice Generator", page_icon="📄", layout="centered")

# CSS to make the app look clean and professional
st.markdown("""
    <style>
    .main-title {
        font-size: 28px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 18px;
        font-weight: bold;
        color: #1F2937;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Radiant Alliance Limited</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #6B7280; margin-bottom: 30px;">Invoice & Challan Generator</div>', unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE MEMORY ---
if 'advice_number' not in st.session_state:
    st.session_state.advice_number = 1385

if 'invoice_number' not in st.session_state:
    st.session_state.invoice_number = 2183

if 'product_count' not in st.session_state:
    st.session_state.product_count = 2  

# --- CUSTOMER DATABASE ---
CUSTOMER_DB = {
    "New Customer (Type manually)": {
        "contact_person": "",
        "contact_no": "",
        "delivery_address": ""
    },
    "Mr. Bellal Hossain": {
        "contact_person": "Mr. Bellal Hossain",
        "contact_no": "01936440711",
        "delivery_address": "Aukpara, Ashulia, Savar, Dhaka"
    },
    "Rahman Trading Co.": {
        "contact_person": "Mr. Anisur Rahman",
        "contact_no": "01711223344",
        "delivery_address": "Mogbazar, Dhaka"
    },
    "Solar Tech BD": {
        "contact_person": "Engr. Kamal",
        "contact_no": "01822334455",
        "delivery_address": "CEPZ, Chittagong"
    }
}

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Company Settings")
uploaded_logo = st.sidebar.file_uploader("Upload Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
logo_path = "ral.jpg" if os.path.exists("ral.jpg") else None

if uploaded_logo is not None:
    with open("temp_logo.jpg", "wb") as f:
        f.write(uploaded_logo.getbuffer())
    logo_path = "temp_logo.jpg"

# --- CUSTOMER DETAILS FORM ---
st.markdown('<div class="section-header">Customer Details</div>', unsafe_allow_html=True)

selected_customer = st.selectbox("Select Customer Profile:", list(CUSTOMER_DB.keys()))

default_person = CUSTOMER_DB[selected_customer]["contact_person"]
default_no = CUSTOMER_DB[selected_customer]["contact_no"]
default_address = CUSTOMER_DB[selected_customer]["delivery_address"]

col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("Customer Name", value="" if selected_customer == "New Customer (Type manually)" else selected_customer)
    contact_person = st.text_input("Contact Person", value=default_person)
with col2:
    contact_no = st.text_input("Contact No", value=default_no)
    delivery_address = st.text_input("Delivery Address", value=default_address)

# --- INVOICE METADATA ---
st.markdown('<div class="section-header">Invoice Details</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    advice_no = st.number_input("Advice No", value=st.session_state.advice_number, step=1)
    invoice_no = st.number_input("Invoice No", value=st.session_state.invoice_number, step=1)
    rm_officer = st.text_input("RM (Sales Officer)", value="Mr. Hafiz")
    payment_mode = st.text_input("Payment Mode", value="Cash on Delivery (Factory Received)")
with col4:
    date_val = st.date_input("Date", value=datetime.today())
    challan_no = st.text_input("Delivery Challan No", value="")
    delivery_date_val = st.date_input("Delivery Date", value=datetime.today())
    note = st.text_area("Note (If any)", value="Please call and confirm with Sales Manager before releasing delivery", height=68)

formatted_date = date_val.strftime('%d.%m.%Y')
formatted_delivery_date = delivery_date_val.strftime('%d.%m.%Y')

# --- DYNAMIC PRODUCTS SECTION ---
st.markdown('<div class="section-header">Products & Items</div>', unsafe_allow_html=True)

col_btn1, col_btn2, _ = st.columns([1, 1, 2])
with col_btn1:
    if st.button("➕ Add Row"):
        st.session_state.product_count += 1
with col_btn2:
    if st.button("❌ Remove Row") and st.session_state.product_count > 1:
        st.session_state.product_count -= 1

items_data = []

for i in range(st.session_state.product_count):
    st.markdown(f"**Product #{i+1}**")
    p_col1, p_col2, p_col3, p_col4 = st.columns([1.5, 3, 1.5, 2])
    with p_col1:
        wp = st.number_input("Wp", value=50.0 if i==0 else (20.0 if i==1 else 0.0), key=f"wp_{i}", step=5.0)
    with p_col2:
        desc = st.text_input("Description", value="Wp Solar PV Module" if i < 2 else "", key=f"desc_{i}", placeholder="e.g. Solar PV Module")
    with p_col3:
        qty = st.number_input("Qty", value=2 if i==0 else (1 if i==1 else 0), key=f"qty_{i}", step=1)
    with p_col4:
        rate = st.number_input("Price / Wp", value=27.00, key=f"rate_{i}", step=1.0)
    
    if desc.strip() != "":
        items_data.append({
            "wp": wp,
            "desc": desc,
            "qty": qty,
            "rate": rate
        })

st.markdown("---")

# --- PDF GENERATION ENGINE ---
class PDF(FPDF):
    def header(self):
        if logo_path and os.path.exists(logo_path):
            self.image(logo_path, x=12, y=12, w=186)
            self.set_y(50)  
        else:
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'RADIANT ALLIANCE LIMITED', ln=True, align='C')
            self.ln(10)

def generate_pdf_file():
    pdf = PDF()
    pdf.set_margins(12, 15, 12)
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(51, 51, 51)
    
    # Left Details Block
    details_left = [
        ("Customer Name:", customer_name),
        ("Contact Person:", contact_person),
        ("Contact No:", contact_no),
        ("Delivery Address:", delivery_address)
    ]
    
    for label, val in details_left:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(35, 6, label, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, val, 0, 1)
        
    pdf.ln(5)
    
    y_before = pdf.get_y()
    right_column_x = 130  # Shifted right, all lines start exactly here for a clean left edge
    
    # --- Column 1 (Left-side Metadata) ---
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(19, 6, "Advice No:", 0, 0) 
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, f" {advice_no}", 0, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(20, 6, "Invoice No:", 0, 0) 
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, f" {invoice_no}", 0, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(8, 6, "RM:", 0, 0) 
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, f" {rm_officer}", 0, 1)
    
    # --- Column 2 (Left Aligned within the Right Side) ---
    # Row 1: Date
    pdf.set_xy(right_column_x, y_before)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(9, 6, "Date:", 0, 0) 
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, f" {formatted_date}", 0, 1)
    
    # Row 2: Delivery Challan No
    pdf.set_xy(right_column_x, y_before + 6)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(35, 6, "Delivery Challan No:", 0, 0) 
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, f" {challan_no}", 0, 1)
    
    # Row 3: Delivery Date
    pdf.set_xy(right_column_x, y_before + 12)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(24, 6, "Delivery Date:", 0, 0) 
    pdf.set_font('Arial', '', 10)
    pdf.cell(45, 6, f" {formatted_delivery_date}", 0, 1)
    
    pdf.set_xy(12, y_before + 18) 
    pdf.ln(4)
    
    # Table headers
    headers = ["SL", "Item In Wp", "Item Description", "Qty", "Price/Wp", "Unit Price", "Total Price"]
    widths = [10, 22, 54, 12, 22, 28, 38]
    alignments = ['C', 'C', 'L', 'C', 'R', 'R', 'R']
    
    pdf.set_fill_color(242, 242, 242)
    pdf.set_font('Arial', 'B', 9)
    for h, w, align in zip(headers, widths, alignments):
        pdf.cell(w, 8, h, 1, 0, align, fill=True)
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    total_qty = 0
    total_price = 0.0
    
    for idx, item in enumerate(items_data, 1):
        unit_price = item["wp"] * item["rate"]
        row_total = item["qty"] * unit_price
        total_qty += item["qty"]
        total_price += row_total
        
        row_data = [
            str(idx),
            f"{item['wp']:g}",
            item["desc"],
            str(item["qty"]),
            f"{item['rate']:,.2f}",
            f"{unit_price:,.2f}",
            f"{row_total:,.2f}"
        ]
        
        for val, w, align in zip(row_data, widths, alignments):
            pdf.cell(w, 8, val, 1, 0, align)
        pdf.ln()
        
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(widths[0] + widths[1] + widths[2], 8, "TOTAL", 1, 0, 'C', fill=True)
    pdf.cell(widths[3], 8, str(total_qty), 1, 0, 'C', fill=True)
    pdf.cell(widths[4], 8, "", 1, 0, 'C', fill=True)
    pdf.cell(widths[5], 8, "", 1, 0, 'C', fill=True)
    pdf.cell(widths[6], 8, f"{total_price:,.2f}", 1, 1, 'R', fill=True)
    
    pdf.ln(8)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, f"Payment Mode: *{payment_mode}", 0, 1)
    
    pdf.ln(12)
    
    y_sig = pdf.get_y()
    pdf.line(12, y_sig, 62, y_sig)
    pdf.line(138, y_sig, 198, y_sig)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, "Prepared By", 0, 0, 'C')
    pdf.cell(76, 6, "", 0, 0)
    pdf.cell(60, 6, "Head of Sales & Marketing", 0, 1, 'C')
    
    pdf.ln(10)
    
    y_app = pdf.get_y()
    pdf.line(83, y_app + 8, 123, y_app + 8)
    pdf.cell(0, 6, "Approved By:", 0, 1, 'C')
    
    pdf.ln(15)
    
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 5, "Note (If any):", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, f"1. {note}")
    
    return bytes(pdf.output())

def increment_counters():
    st.session_state.advice_number = advice_no + 1
    st.session_state.invoice_number = invoice_no + 1

if len(items_data) == 0:
    st.warning("⚠️ Please fill out at least one product row with a description.")
else:
    pdf_bytes = generate_pdf_file()
    
    safe_customer_name = customer_name.strip().replace(" ", "_") if customer_name else "Unknown_Customer"
    dynamic_filename = f"DA_{safe_customer_name}_{formatted_date}.pdf"
    
    st.download_button(
        label="⚡ Generate & Download PDF Instantly",
        data=pdf_bytes,
        file_name=dynamic_filename,
        mime="application/pdf",
        use_container_width=True,
        on_click=increment_counters 
    )
