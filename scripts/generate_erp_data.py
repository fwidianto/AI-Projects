"""
ERP Analytics Platform - Data Generation Script
Generates realistic ERP data for a fictional distribution company
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
import hashlib

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Ensure directories exist
for d in [DATABASE_DIR, DATA_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

DB_PATH = os.path.join(DATABASE_DIR, 'erp_database.db')

# Date range for transactions (24 months)
END_DATE = datetime(2025, 6, 30)
START_DATE = datetime(2023, 7, 1)

# ========================================
# MASTER DATA DEFINITIONS
# ========================================

PRODUCT_CATEGORIES = [
    'Electronics', 'Office Supplies', 'Industrial Equipment', 'Safety Equipment',
    'Packaging Materials', 'Cleaning Supplies', 'Computer Hardware', 'Tools',
    'Furniture', 'Lighting', 'Plumbing', 'Electrical', 'HVAC', 'Security',
    'Medical Supplies', 'Laboratory Equipment'
]

SUPPLIER_TYPES = ['Manufacturer', 'Distributor', 'Importer', 'Wholesaler']

INDUSTRIES = [
    'Manufacturing', 'Retail', 'Healthcare', 'Education', 'Construction',
    'Hospitality', 'Transportation', 'Technology', 'Agriculture', 'Government',
    'Finance', 'Real Estate', 'Consulting', 'Media', 'Energy'
]

REGIONS = ['North', 'South', 'East', 'West', 'Central']

COUNTRIES = [
    'United States', 'Canada', 'Mexico', 'Germany', 'United Kingdom',
    'France', 'Italy', 'Spain', 'China', 'Japan', 'South Korea',
    'India', 'Brazil', 'Australia', 'Netherlands'
]

# ========================================
# UTILITY FUNCTIONS
# ========================================

def random_date(start, end):
    """Generate random date between start and end"""
    delta = end - start
    int_delta = delta.days
    random_days = random.randint(0, int_delta)
    return start + timedelta(days=random_days)

def generate_id(prefix, number):
    """Generate formatted ID"""
    return f"{prefix}-{number:08d}"

def generate_po_number(number):
    return f"PO-{number:08d}"

def generate_so_number(number):
    return f"SO-{number:08d}"

def generate_receipt_number(number):
    return f"GR-{number:08d}"

def generate_delivery_number(number):
    return f"DO-{number:08d}"

def generate_invoice_number(number):
    return f"INV-{number:08d}"

def generate_payment_number(number):
    return f"PAY-{number:08d}"

def generate_quotation_number(number):
    return f"QUO-{number:08d}"

def generate_lead_id(number):
    return f"LEAD-{number:08d}"

# ========================================
# DATABASE SETUP
# ========================================

def setup_database():
    """Create all tables with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables (excluding internal SQLite tables)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
    
    # ========================================
    # MASTER DATA TABLES
    # ========================================
    
    # Products
    cursor.execute('''
        CREATE TABLE dim_product (
            product_id TEXT PRIMARY KEY,
            sku TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            default_selling_price REAL NOT NULL,
            unit_cost REAL,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Suppliers
    cursor.execute('''
        CREATE TABLE dim_supplier (
            supplier_id TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            country TEXT NOT NULL,
            supplier_type TEXT NOT NULL,
            contact_name TEXT,
            email TEXT,
            phone TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Customers
    cursor.execute('''
        CREATE TABLE dim_customer (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            region TEXT NOT NULL,
            country TEXT,
            credit_limit REAL DEFAULT 10000,
            payment_terms_days INTEGER DEFAULT 30,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Salespersons
    cursor.execute('''
        CREATE TABLE dim_salesperson (
            salesperson_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            region TEXT,
            hire_date DATE
        )
    ''')
    
    # Warehouses
    cursor.execute('''
        CREATE TABLE dim_warehouse (
            warehouse_id TEXT PRIMARY KEY,
            warehouse_name TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER,
            manager_name TEXT
        )
    ''')
    
    # Date Dimension
    cursor.execute('''
        CREATE TABLE dim_date (
            date_id TEXT PRIMARY KEY,
            full_date DATE UNIQUE NOT NULL,
            day_of_week INTEGER,
            day_name TEXT,
            day_of_month INTEGER,
            day_of_year INTEGER,
            week_of_year INTEGER,
            month INTEGER,
            month_name TEXT,
            quarter INTEGER,
            year INTEGER,
            is_weekend INTEGER,
            is_holiday INTEGER,
            fiscal_year INTEGER,
            fiscal_quarter INTEGER
        )
    ''')
    
    # ========================================
    # PROCURE TO PAY TABLES
    # ========================================
    
    # Purchase Orders
    cursor.execute('''
        CREATE TABLE fact_purchase_orders (
            po_id TEXT PRIMARY KEY,
            po_number TEXT UNIQUE NOT NULL,
            supplier_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            order_date DATE NOT NULL,
            expected_receipt_date DATE,
            actual_receipt_date DATE,
            status TEXT DEFAULT 'PENDING',
            created_by TEXT,
            FOREIGN KEY (supplier_id) REFERENCES dim_supplier(supplier_id),
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
        )
    ''')
    
    # Goods Receipts
    cursor.execute('''
        CREATE TABLE fact_goods_receipts (
            receipt_id TEXT PRIMARY KEY,
            receipt_number TEXT UNIQUE NOT NULL,
            po_id TEXT NOT NULL,
            receipt_date DATE NOT NULL,
            quantity_received INTEGER NOT NULL,
            warehouse_id TEXT NOT NULL,
            quality_check_passed INTEGER DEFAULT 1,
            notes TEXT,
            FOREIGN KEY (po_id) REFERENCES fact_purchase_orders(po_id),
            FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
        )
    ''')
    
    # ========================================
    # ORDER TO CASH TABLES
    # ========================================
    
    # CRM Leads
    cursor.execute('''
        CREATE TABLE fact_crm_leads (
            lead_id TEXT PRIMARY KEY,
            lead_number TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            salesperson_id TEXT NOT NULL,
            estimated_value REAL,
            lead_date DATE NOT NULL,
            lead_status TEXT DEFAULT 'NEW',
            source TEXT,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
            FOREIGN KEY (salesperson_id) REFERENCES dim_salesperson(salesperson_id)
        )
    ''')
    
    # Sales Quotations
    cursor.execute('''
        CREATE TABLE fact_sales_quotations (
            quotation_id TEXT PRIMARY KEY,
            quotation_number TEXT UNIQUE NOT NULL,
            lead_id TEXT,
            customer_id TEXT NOT NULL,
            salesperson_id TEXT NOT NULL,
            amount REAL NOT NULL,
            quotation_date DATE NOT NULL,
            valid_until_date DATE,
            status TEXT DEFAULT 'DRAFT',
            notes TEXT,
            FOREIGN KEY (lead_id) REFERENCES fact_crm_leads(lead_id),
            FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
            FOREIGN KEY (salesperson_id) REFERENCES dim_salesperson(salesperson_id)
        )
    ''')
    
    # Sales Orders
    cursor.execute('''
        CREATE TABLE fact_sales_orders (
            so_id TEXT PRIMARY KEY,
            so_number TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            order_date DATE NOT NULL,
            expected_delivery_date DATE,
            actual_delivery_date DATE,
            status TEXT DEFAULT 'CONFIRMED',
            salesperson_id TEXT,
            warehouse_id TEXT,
            so_type TEXT DEFAULT 'STANDARD',
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
            FOREIGN KEY (salesperson_id) REFERENCES dim_salesperson(salesperson_id),
            FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
        )
    ''')
    
    # Delivery Orders
    cursor.execute('''
        CREATE TABLE fact_delivery_orders (
            delivery_id TEXT PRIMARY KEY,
            delivery_number TEXT UNIQUE NOT NULL,
            so_id TEXT NOT NULL,
            delivery_date DATE NOT NULL,
            quantity_delivered INTEGER NOT NULL,
            warehouse_id TEXT NOT NULL,
            driver_name TEXT,
            vehicle_number TEXT,
            notes TEXT,
            FOREIGN KEY (so_id) REFERENCES fact_sales_orders(so_id),
            FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
        )
    ''')
    
    # Customer Invoices
    cursor.execute('''
        CREATE TABLE fact_customer_invoices (
            invoice_id TEXT PRIMARY KEY,
            invoice_number TEXT UNIQUE NOT NULL,
            so_id TEXT NOT NULL,
            invoice_date DATE NOT NULL,
            due_date DATE NOT NULL,
            total_amount REAL NOT NULL,
            amount_paid REAL DEFAULT 0,
            status TEXT DEFAULT 'OPEN',
            payment_terms_days INTEGER DEFAULT 30,
            FOREIGN KEY (so_id) REFERENCES fact_sales_orders(so_id)
        )
    ''')
    
    # Customer Payments
    cursor.execute('''
        CREATE TABLE fact_customer_payments (
            payment_id TEXT PRIMARY KEY,
            payment_number TEXT UNIQUE NOT NULL,
            invoice_id TEXT NOT NULL,
            payment_date DATE NOT NULL,
            amount_paid REAL NOT NULL,
            payment_method TEXT,
            reference_number TEXT,
            notes TEXT,
            FOREIGN KEY (invoice_id) REFERENCES fact_customer_invoices(invoice_id)
        )
    ''')
    
    # ========================================
    # INVENTORY TABLES
    # ========================================
    
    # Inventory Ledger (FIFO tracking)
    cursor.execute('''
        CREATE TABLE fact_inventory_ledger (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            warehouse_id TEXT NOT NULL,
            movement_date DATE NOT NULL,
            movement_type TEXT NOT NULL,
            reference_type TEXT,
            reference_id TEXT,
            quantity_in INTEGER DEFAULT 0,
            quantity_out INTEGER DEFAULT 0,
            unit_cost REAL,
            running_balance INTEGER,
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
            FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
        )
    ''')
    
    # Current Inventory Snapshot
    cursor.execute('''
        CREATE TABLE fact_current_inventory (
            product_id TEXT NOT NULL,
            warehouse_id TEXT NOT NULL,
            quantity_on_hand INTEGER DEFAULT 0,
            average_cost REAL,
            last_updated DATE,
            PRIMARY KEY (product_id, warehouse_id),
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
            FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
        )
    ''')
    
    # ========================================
    # COSTING TABLES
    # ========================================
    
    # Sales Profitability (calculated from actual costs)
    cursor.execute('''
        CREATE TABLE fact_sales_profitability (
            profitability_id INTEGER PRIMARY KEY AUTOINCREMENT,
            so_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity_sold INTEGER NOT NULL,
            revenue REAL NOT NULL,
            cost_of_goods_sold REAL NOT NULL,
            gross_profit REAL NOT NULL,
            gross_margin_pct REAL NOT NULL,
            calculation_date DATE,
            FOREIGN KEY (so_id) REFERENCES fact_sales_orders(so_id),
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
        )
    ''')
    
    conn.commit()
    print("Database schema created successfully!")
    return conn

# ========================================
# MASTER DATA GENERATION
# ========================================

def generate_master_data(conn):
    """Generate all master data records"""
    cursor = conn.cursor()
    
    print("Generating master data...")
    
    # ========================================
    # PRODUCTS (500)
    # ========================================
    print("  - Products (500)")
    products = []
    product_id_counter = 1
    
    product_templates = [
        # Electronics
        ('USB-C Cable', 12.99, 'Electronics'), ('HDMI Cable 6ft', 8.99, 'Electronics'),
        ('Wireless Mouse', 24.99, 'Electronics'), ('Bluetooth Keyboard', 49.99, 'Electronics'),
        ('Webcam HD', 79.99, 'Electronics'), ('USB Hub 7-Port', 34.99, 'Electronics'),
        ('Ethernet Switch 8-Port', 89.99, 'Electronics'), ('Power Strip 6-Outlet', 19.99, 'Electronics'),
        ('Surge Protector', 29.99, 'Electronics'), ('Laptop Stand', 45.99, 'Electronics'),
        # Office Supplies
        ('A4 Paper Ream', 7.99, 'Office Supplies'), ('Ballpoint Pens 12-Pack', 5.99, 'Office Supplies'),
        ('Sticky Notes 3x3', 4.99, 'Office Supplies'), ('File Folders 100-Pack', 12.99, 'Office Supplies'),
        ('Stapler Heavy Duty', 24.99, 'Office Supplies'), ('Paper Clips Box', 2.99, 'Office Supplies'),
        ('Binder Clips Assorted', 3.99, 'Office Supplies'), ('Desk Organizer', 19.99, 'Office Supplies'),
        ('Whiteboard 24x36', 49.99, 'Office Supplies'), ('Dry Erase Markers', 8.99, 'Office Supplies'),
        # Computer Hardware
        ('SSD 500GB', 89.99, 'Computer Hardware'), ('RAM 16GB DDR4', 69.99, 'Computer Hardware'),
        ('Mechanical Keyboard', 129.99, 'Computer Hardware'), ('Monitor 27 inch', 349.99, 'Computer Hardware'),
        ('Graphics Card Entry', 199.99, 'Computer Hardware'), ('CPU Cooler', 45.99, 'Computer Hardware'),
        ('PC Case Mid Tower', 79.99, 'Computer Hardware'), ('Power Supply 650W', 89.99, 'Computer Hardware'),
        ('Motherboard B550', 179.99, 'Computer Hardware'), ('NVMe Cable', 12.99, 'Computer Hardware'),
        # Tools
        ('Drill Driver Cordless', 149.99, 'Tools'), ('Socket Set 40-Piece', 79.99, 'Tools'),
        ('Measuring Tape 25ft', 14.99, 'Tools'), ('Level 24 inch', 34.99, 'Tools'),
        ('Screwdriver Set 100pc', 49.99, 'Tools'), ('Wrench Set Adjustable', 39.99, 'Tools'),
        ('Pliers Set 5-Piece', 29.99, 'Tools'), ('Hammer 16oz', 19.99, 'Tools'),
        ('Tape Measure Digital', 24.99, 'Tools'), ('Utility Knife', 8.99, 'Tools'),
    ]
    
    for i in range(500):
        template_idx = i % len(product_templates)
        base_name, base_price, category = product_templates[template_idx]
        
        if i >= len(product_templates):
            # Create variations
            suffix = random.choice(['Pro', 'Plus', 'XL', 'HD', 'Max', 'Lite', 'Basic', 'Premium'])
            name = f"{base_name} {suffix}"
        else:
            name = base_name
        
        sku = f"SKU-{i+1:05d}"
        product_id = generate_id("PRD", product_id_counter)
        product_id_counter += 1
        
        # Add some price variation
        price_variation = random.uniform(0.85, 1.15)
        selling_price = round(base_price * price_variation, 2)
        
        products.append((product_id, sku, name, category, selling_price))
    
    cursor.executemany(
        "INSERT INTO dim_product (product_id, sku, product_name, category, default_selling_price) VALUES (?, ?, ?, ?, ?)",
        products
    )
    
    # ========================================
    # SUPPLIERS (100)
    # ========================================
    print("  - Suppliers (100)")
    suppliers = []
    
    supplier_names = [
        'Global Tech Supply', 'Prime Industrial', 'FastParts Direct', 'QualitySource Inc',
        'Reliable Components', 'Premier Materials', 'ValueFirst Supply', 'Alliance Trading',
        'Summit Distribution', 'Peak Performance', 'Elite Imports', 'Advanced Logistics',
        'Central Supplies', 'United Parts', 'National Distribution', 'Pacific Trading Co',
        'Atlantic Supply', 'Mountain Components', 'Valley Industrial', 'Coastal Distributors'
    ]
    
    for i in range(100):
        supplier_id = generate_id("SUP", i+1)
        name_base = supplier_names[i % len(supplier_names)]
        supplier_name = f"{name_base} #{i+1}" if i >= len(supplier_names) else name_base
        
        country = random.choice(COUNTRIES)
        supplier_type = random.choice(SUPPLIER_TYPES)
        contact_name = fake.name()
        email = fake.company_email()
        phone = fake.phone_number()
        
        suppliers.append((supplier_id, supplier_name, country, supplier_type, contact_name, email, phone))
    
    cursor.executemany(
        "INSERT INTO dim_supplier (supplier_id, supplier_name, country, supplier_type, contact_name, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
        suppliers
    )
    
    # ========================================
    # CUSTOMERS (1000)
    # ========================================
    print("  - Customers (1000)")
    customers = []
    
    customer_names = [
        'Acme Corp', 'TechStart Inc', 'Global Solutions', 'Metro Services', 'Premier Industries',
        'Sunrise Enterprises', 'Pinnacle Group', 'Horizon Tech', 'Summit Partners', 'Valley Systems',
        'Coastal Manufacturing', 'Mountain Logistics', 'Central Trading', 'Eastern Supplies',
        'Western Distributors', 'Northern Holdings', 'Southern Ventures', 'Atlas Corporation',
        'Titan Industries', 'Omega Enterprises'
    ]
    
    for i in range(1000):
        customer_id = generate_id("CUST", i+1)
        
        if i < len(customer_names):
            customer_name = customer_names[i]
        else:
            # Generate variation
            suffix = random.choice(['LLC', 'Inc', 'Corp', 'Co', 'Ltd'])
            customer_name = f"{fake.company()[:30]} {suffix}"
        
        industry = random.choice(INDUSTRIES)
        region = random.choice(REGIONS)
        country = random.choice(['United States', 'Canada', 'Mexico'])
        credit_limit = random.choice([5000, 10000, 25000, 50000, 100000])
        payment_terms_days = random.choice([15, 30, 45, 60])
        
        customers.append((customer_id, customer_name, industry, region, country, credit_limit, payment_terms_days))
    
    cursor.executemany(
        "INSERT INTO dim_customer (customer_id, customer_name, industry, region, country, credit_limit, payment_terms_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
        customers
    )
    
    # ========================================
    # SALESPERSONS (20)
    # ========================================
    print("  - Salespersons (20)")
    salespersons = []
    
    for i in range(20):
        salesperson_id = generate_id("SP", i+1)
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@company.com"
        phone = fake.phone_number()
        region = random.choice(REGIONS)
        hire_date = random_date(datetime(2022, 1, 1), datetime(2023, 6, 30)).strftime('%Y-%m-%d')
        
        salespersons.append((salesperson_id, first_name, last_name, email, phone, region, hire_date))
    
    cursor.executemany(
        "INSERT INTO dim_salesperson (salesperson_id, first_name, last_name, email, phone, region, hire_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        salespersons
    )
    
    # ========================================
    # WAREHOUSES (3)
    # ========================================
    print("  - Warehouses (3)")
    warehouses = [
        ("WH-001", "Main Distribution Center", "Chicago, IL", 50000, "John Smith"),
        ("WH-002", "East Coast Hub", "Newark, NJ", 35000, "Maria Garcia"),
        ("WH-003", "West Coast Center", "Los Angeles, CA", 40000, "David Chen")
    ]
    
    cursor.executemany(
        "INSERT INTO dim_warehouse (warehouse_id, warehouse_name, location, capacity, manager_name) VALUES (?, ?, ?, ?, ?)",
        warehouses
    )
    
    # ========================================
    # DATE DIMENSION (24 months)
    # ========================================
    print("  - Date Dimension")
    dates = []
    current = START_DATE
    
    while current <= END_DATE:
        date_id = current.strftime('%Y%m%d')
        fiscal_year = current.year if current.month >= 7 else current.year - 1
        fiscal_quarter = ((current.month - 7) // 3 + 4) % 4 + 1
        
        dates.append((
            date_id,
            current.strftime('%Y-%m-%d'),
            current.weekday(),
            current.strftime('%A'),
            current.day,
            current.timetuple().tm_yday,
            current.isocalendar()[1],
            current.month,
            current.strftime('%B'),
            (current.month - 1) // 3 + 1,
            current.year,
            1 if current.weekday() >= 5 else 0,
            0,  # is_holiday - simplified
            fiscal_year,
            fiscal_quarter
        ))
        current += timedelta(days=1)
    
    cursor.executemany(
        "INSERT INTO dim_date (date_id, full_date, day_of_week, day_name, day_of_month, day_of_year, week_of_year, month, month_name, quarter, year, is_weekend, is_holiday, fiscal_year, fiscal_quarter) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        dates
    )
    
    conn.commit()
    print("Master data generation complete!")
    return products, suppliers, customers, salespersons

# ========================================
# PROCURE TO PAY GENERATION
# ========================================

def generate_procure_to_pay(conn, products, suppliers):
    """Generate purchase orders and goods receipts"""
    cursor = conn.cursor()
    
    print("Generating Procure-to-Pay data...")
    
    # Create product-supplier relationships (each product has 1-3 suppliers)
    product_suppliers = {}
    for product in products:
        product_id = product[0]
        num_suppliers = random.randint(1, 3)
        selected_suppliers = random.sample(suppliers, min(num_suppliers, len(suppliers)))
        product_suppliers[product_id] = selected_suppliers
    
    purchase_orders = []
    goods_receipts = []
    po_counter = 1
    receipt_counter = 1
    
    # Generate 5000+ Purchase Orders
    print("  - Purchase Orders (5000+)")
    
    for i in range(5500):
        po_id = f"PO-{po_counter:08d}"
        po_number = generate_po_number(po_counter)
        po_counter += 1
        
        # Select product and supplier
        product = random.choice(products)
        product_id = product[0]
        available_suppliers = product_suppliers.get(product_id, suppliers)
        supplier = random.choice(available_suppliers)
        supplier_id = supplier[0]
        
        quantity = random.choice([10, 20, 25, 50, 75, 100, 150, 200])
        
        # Cost variation based on supplier
        base_price = product[4]  # default_selling_price
        cost_variation = random.uniform(0.5, 0.7)  # Suppliers sell at 50-70% of selling price
        unit_cost = round(base_price * cost_variation, 2)
        
        total_cost = quantity * unit_cost
        
        order_date = random_date(START_DATE, END_DATE - timedelta(days=30))
        expected_receipt = order_date + timedelta(days=random.randint(7, 30))
        
        # Most POs are completed, some pending, few cancelled
        status = random.choices(['COMPLETED', 'PENDING', 'CANCELLED'], weights=[85, 12, 3])[0]
        
        purchase_orders.append((
            po_id, po_number, supplier_id, product_id, quantity, unit_cost, total_cost,
            order_date.strftime('%Y-%m-%d'), expected_receipt.strftime('%Y-%m-%d'),
            None if status != 'COMPLETED' else (expected_receipt + timedelta(days=random.randint(-5, 10))).strftime('%Y-%m-%d'),
            status, None
        ))
    
    cursor.executemany(
        "INSERT INTO fact_purchase_orders (po_id, po_number, supplier_id, product_id, quantity, unit_cost, total_cost, order_date, expected_receipt_date, actual_receipt_date, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        purchase_orders
    )
    
    # Generate Goods Receipts for completed POs
    print("  - Goods Receipts")
    
    # Get completed POs
    cursor.execute("SELECT po_id, product_id, quantity, order_date, actual_receipt_date FROM fact_purchase_orders WHERE status = 'COMPLETED'")
    completed_pos = cursor.fetchall()
    
    for po in completed_pos:
        po_id, product_id, quantity, order_date, actual_date = po
        
        # Some POs have partial receipts (1-3 receipts per PO)
        num_receipts = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
        
        remaining_qty = quantity
        receipt_dates = []
        
        for r in range(num_receipts):
            receipt_id = f"GR-{receipt_counter:08d}"
            receipt_number = generate_receipt_number(receipt_counter)
            receipt_counter += 1
            
            if r == num_receipts - 1:
                # Last receipt - deliver remaining
                qty_received = remaining_qty
            else:
                # Partial receipt
                qty_received = random.randint(1, remaining_qty // 2) if remaining_qty > 1 else 1
            
            # Receipt date based on actual delivery
            if actual_date:
                base_date = datetime.strptime(actual_date, '%Y-%m-%d')
                receipt_date = base_date + timedelta(days=random.randint(-3, 3))
            else:
                receipt_date = datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=random.randint(7, 30))
            
            receipt_dates.append(receipt_date)
            
            warehouse_id = random.choice(["WH-001", "WH-002", "WH-003"])
            quality_check = random.choices([1, 0], weights=[95, 5])[0]
            
            goods_receipts.append((
                receipt_id, receipt_number, po_id, receipt_date.strftime('%Y-%m-%d'),
                qty_received, warehouse_id, quality_check, None
            ))
            
            remaining_qty -= qty_received
            if remaining_qty <= 0:
                break
    
    cursor.executemany(
        "INSERT INTO fact_goods_receipts (receipt_id, receipt_number, po_id, receipt_date, quantity_received, warehouse_id, quality_check_passed, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        goods_receipts
    )
    
    conn.commit()
    print(f"  Generated {len(purchase_orders)} Purchase Orders")
    print(f"  Generated {len(goods_receipts)} Goods Receipts")
    
    return goods_receipts

# ========================================
# INVENTORY PROCESSING
# ========================================

def process_inventory_movements(conn, goods_receipts):
    """Process goods receipts into inventory ledger"""
    cursor = conn.cursor()
    
    print("Processing inventory movements...")
    
    # Get all goods receipts with their costs
    cursor.execute('''
        SELECT gr.receipt_id, gr.receipt_number, po.product_id, gr.warehouse_id, gr.quantity_received, gr.receipt_date, po.unit_cost
        FROM fact_goods_receipts gr
        JOIN fact_purchase_orders po ON gr.po_id = po.po_id
    ''')
    receipts = cursor.fetchall()
    
    inventory_movements = []
    
    for receipt in receipts:
        receipt_id, receipt_number, product_id, warehouse_id, qty, date_str, unit_cost = receipt
        
        inventory_movements.append((
            product_id, warehouse_id, date_str, 'GOODS_RECEIPT', 'GOODS_RECEIPT', receipt_id,
            qty, 0, unit_cost, None
        ))
    
    cursor.executemany(
        "INSERT INTO fact_inventory_ledger (product_id, warehouse_id, movement_date, movement_type, reference_type, reference_id, quantity_in, quantity_out, unit_cost, running_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        inventory_movements
    )
    
    conn.commit()
    print(f"  Processed {len(inventory_movements)} inventory movements from receipts")
    
    # Update running balances
    cursor.execute('''
        SELECT movement_id, product_id, warehouse_id, quantity_in, quantity_out, unit_cost
        FROM fact_inventory_ledger
        ORDER BY product_id, warehouse_id, movement_date, movement_id
    ''')
    movements = cursor.fetchall()
    
    # Calculate running balances
    balance_cache = {}  # (product_id, warehouse_id) -> balance
    updated_movements = []
    
    for m in movements:
        movement_id, product_id, warehouse_id, qty_in, qty_out, unit_cost = m
        key = (product_id, warehouse_id)
        
        current_balance = balance_cache.get(key, 0)
        new_balance = current_balance + qty_in - qty_out
        balance_cache[key] = new_balance
        
        updated_movements.append((new_balance, movement_id))
    
    cursor.executemany(
        "UPDATE fact_inventory_ledger SET running_balance = ? WHERE movement_id = ?",
        updated_movements
    )
    
    conn.commit()
    print("  Updated running balances")

# ========================================
# ORDER TO CASH GENERATION
# ========================================

def generate_order_to_cash(conn, products, customers, salespersons):
    """Generate CRM leads, quotations, sales orders, deliveries, invoices, payments"""
    cursor = conn.cursor()
    
    print("Generating Order-to-Cash data...")
    
    leads = []
    quotations = []
    sales_orders = []
    delivery_orders = []
    invoices = []
    payments = []
    
    lead_counter = 1
    quo_counter = 1
    so_counter = 1
    do_counter = 1
    inv_counter = 1
    pay_counter = 1
    
    # ========================================
    # CRM LEADS (3000)
    # ========================================
    print("  - CRM Leads")
    
    for i in range(3000):
        lead_id = generate_lead_id(lead_counter)
        lead_number = f"LEAD-{lead_counter:08d}"
        lead_counter += 1
        
        customer = random.choice(customers)
        customer_id = customer[0]
        salesperson = random.choice(salespersons)
        salesperson_id = salesperson[0]
        
        estimated_value = random.choice([500, 1000, 2500, 5000, 10000, 25000, 50000])
        lead_date = random_date(START_DATE, END_DATE).strftime('%Y-%m-%d')
        
        # Lead conversion rates
        status = random.choices(['NEW', 'CONTACTED', 'QUALIFIED', 'CONVERTED', 'LOST'], weights=[20, 30, 25, 15, 10])[0]
        
        source = random.choice(['Website', 'Referral', 'Trade Show', 'Cold Call', 'Email Campaign', 'Partner'])
        
        leads.append((lead_id, lead_number, customer_id, salesperson_id, estimated_value, lead_date, status, source, None))
    
    cursor.executemany(
        "INSERT INTO fact_crm_leads (lead_id, lead_number, customer_id, salesperson_id, estimated_value, lead_date, lead_status, source, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        leads
    )
    
    # ========================================
    # SALES QUOTATIONS (2000)
    # ========================================
    print("  - Sales Quotations")
    
    # Get converted leads
    cursor.execute("SELECT lead_id FROM fact_crm_leads WHERE lead_status IN ('CONVERTED', 'QUALIFIED')")
    converted_leads = [r[0] for r in cursor.fetchall()]
    
    for i in range(2000):
        quotation_id = f"QUO-{quo_counter:08d}"
        quotation_number = generate_quotation_number(quo_counter)
        quo_counter += 1
        
        # Some from leads, some standalone
        if converted_leads and random.random() < 0.6:
            lead_id = random.choice(converted_leads)
            # Get customer from lead
            cursor.execute("SELECT customer_id, salesperson_id FROM fact_crm_leads WHERE lead_id = ?", (lead_id,))
            lead_data = cursor.fetchone()
            customer_id = lead_data[0]
            salesperson_id = lead_data[1]
        else:
            lead_id = None
            customer = random.choice(customers)
            customer_id = customer[0]
            salesperson = random.choice(salespersons)
            salesperson_id = salesperson[0]
        
        # Amount based on product prices
        num_products = random.randint(1, 5)
        amount = sum(random.choice(products)[4] * random.randint(1, 20) for _ in range(num_products))
        
        quotation_date = random_date(START_DATE, END_DATE).strftime('%Y-%m-%d')
        valid_until = (datetime.strptime(quotation_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Quote conversion rates
        status = random.choices(['DRAFT', 'SENT', 'ACCEPTED', 'REJECTED', 'EXPIRED'], weights=[10, 30, 40, 10, 10])[0]
        
        quotations.append((quotation_id, quotation_number, lead_id, customer_id, salesperson_id, round(amount, 2), quotation_date, valid_until, status, None))
    
    cursor.executemany(
        "INSERT INTO fact_sales_quotations (quotation_id, quotation_number, lead_id, customer_id, salesperson_id, amount, quotation_date, valid_until_date, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        quotations
    )
    
    # ========================================
    # SALES ORDERS (10000+)
    # ========================================
    print("  - Sales Orders (10000+)")
    
    # Get accepted quotations
    cursor.execute("SELECT quotation_id, customer_id, salesperson_id, amount FROM fact_sales_quotations WHERE status = 'ACCEPTED'")
    accepted_quotes = cursor.fetchall()
    
    # Also create standalone orders
    for i in range(11000):
        so_id = f"SO-{so_counter:08d}"
        so_number = generate_so_number(so_counter)
        so_counter += 1
        
        # Mix of quotation-based and standalone orders
        if accepted_quotes and random.random() < 0.4:
            quotation_id, customer_id, salesperson_id, total_amount = random.choice(accepted_quotes)
        else:
            customer = random.choice(customers)
            customer_id = customer[0]
            salesperson = random.choice(salespersons)
            salesperson_id = salesperson[0]
        
        # Select product
        product = random.choice(products)
        product_id = product[0]
        
        # Check inventory availability
        cursor.execute('''
            SELECT COALESCE(SUM(quantity_in - quantity_out), 0) as available
            FROM fact_inventory_ledger
            WHERE product_id = ?
        ''', (product_id,))
        available = cursor.fetchone()[0] or 0
        
        if available < 5:
            # Low inventory - skip or reduce quantity
            if random.random() < 0.3:
                continue
        
        quantity = random.choice([1, 2, 5, 10, 15, 20, 25, 50])
        quantity = min(quantity, max(1, available // 2))  # Don't exceed available
        
        selling_price = product[4]  # default selling price
        # Price variation for discounts
        if random.random() < 0.3:
            selling_price = selling_price * random.uniform(0.85, 0.95)
        
        total_amount = round(quantity * selling_price, 2)
        
        order_date = random_date(START_DATE, END_DATE).strftime('%Y-%m-%d')
        expected_delivery = (datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=random.randint(3, 14))).strftime('%Y-%m-%d')
        
        # Order status distribution
        status = random.choices(['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'], weights=[30, 25, 20, 20, 5])[0]
        
        warehouse_id = random.choice(["WH-001", "WH-002", "WH-003"])
        
        sales_orders.append((
            so_id, so_number, customer_id, product_id, quantity, round(selling_price, 2), total_amount,
            order_date, expected_delivery, None, status, salesperson_id, warehouse_id, 'STANDARD', None
        ))
    
    cursor.executemany(
        "INSERT INTO fact_sales_orders (so_id, so_number, customer_id, product_id, quantity, unit_price, total_amount, order_date, expected_delivery_date, actual_delivery_date, status, salesperson_id, warehouse_id, so_type, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        sales_orders
    )
    
    # ========================================
    # DELIVERY ORDERS
    # ========================================
    print("  - Delivery Orders")
    
    # Get non-cancelled sales orders
    cursor.execute("SELECT so_id, product_id, quantity, warehouse_id, order_date, expected_delivery_date FROM fact_sales_orders WHERE status != 'CANCELLED'")
    active_orders = cursor.fetchall()
    
    for order in active_orders:
        so_id, product_id, quantity, warehouse_id, order_date, expected_date = order
        
        # Most orders are delivered, some partially, some delayed
        num_deliveries = random.choices([1, 2], weights=[75, 25])[0]
        
        remaining_qty = quantity
        base_date = datetime.strptime(expected_date, '%Y-%m-%d')
        
        for d in range(num_deliveries):
            delivery_id = f"DO-{do_counter:08d}"
            delivery_number = generate_delivery_number(do_counter)
            do_counter += 1
            
            if d == num_deliveries - 1:
                qty_delivered = remaining_qty
            else:
                qty_delivered = random.randint(1, remaining_qty // 2) if remaining_qty > 1 else 1
            
            # Some delayed deliveries
            if random.random() < 0.15:
                delivery_date = base_date + timedelta(days=random.randint(1, 7))
            else:
                delivery_date = base_date + timedelta(days=random.randint(-2, 2))
            
            driver_name = fake.name()
            vehicle_number = f"{random.choice(['ABC', 'XYZ', 'TRK'])}-{random.randint(1000, 9999)}"
            
            delivery_orders.append((
                delivery_id, delivery_number, so_id, delivery_date.strftime('%Y-%m-%d'),
                qty_delivered, warehouse_id, driver_name, vehicle_number, None
            ))
            
            remaining_qty -= qty_delivered
            if remaining_qty <= 0:
                break
    
    cursor.executemany(
        "INSERT INTO fact_delivery_orders (delivery_id, delivery_number, so_id, delivery_date, quantity_delivered, warehouse_id, driver_name, vehicle_number, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        delivery_orders
    )
    
    # ========================================
    # CUSTOMER INVOICES
    # ========================================
    print("  - Customer Invoices")
    
    # Get delivered/confirmed orders
    cursor.execute("SELECT so_id, customer_id, total_amount, order_date FROM fact_sales_orders WHERE status IN ('CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED')")
    billable_orders = cursor.fetchall()
    
    for order in billable_orders:
        so_id, customer_id, total_amount, order_date = order
        
        # Get customer payment terms
        cursor.execute("SELECT payment_terms_days FROM dim_customer WHERE customer_id = ?", (customer_id,))
        payment_terms = cursor.fetchone()[0] or 30
        
        invoice_id = f"INV-{inv_counter:08d}"
        invoice_number = generate_invoice_number(inv_counter)
        inv_counter += 1
        
        invoice_date = (datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d')
        due_date = (datetime.strptime(invoice_date, '%Y-%m-%d') + timedelta(days=payment_terms)).strftime('%Y-%m-%d')
        
        # Invoice status
        status = random.choices(['OPEN', 'PARTIAL', 'PAID', 'OVERDUE'], weights=[40, 15, 35, 10])[0]
        
        # Some partial payments
        if status == 'PARTIAL':
            amount_paid = round(total_amount * random.uniform(0.3, 0.7), 2)
        elif status == 'PAID':
            amount_paid = total_amount
        else:
            amount_paid = 0
        
        invoices.append((
            invoice_id, invoice_number, so_id, invoice_date, due_date,
            total_amount, amount_paid, status, payment_terms
        ))
    
    cursor.executemany(
        "INSERT INTO fact_customer_invoices (invoice_id, invoice_number, so_id, invoice_date, due_date, total_amount, amount_paid, status, payment_terms_days) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        invoices
    )
    
    # ========================================
    # CUSTOMER PAYMENTS
    # ========================================
    print("  - Customer Payments")
    
    # Get non-open invoices
    cursor.execute("SELECT invoice_id, total_amount, due_date FROM fact_customer_invoices WHERE status IN ('PAID', 'PARTIAL', 'OVERDUE')")
    payable_invoices = cursor.fetchall()
    
    for invoice in payable_invoices:
        invoice_id, total_amount, due_date = invoice
        
        # Most pay on time, some late
        if random.random() < 0.7:
            # Pay on time
            payment_date = (datetime.strptime(due_date, '%Y-%m-%d') - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d')
        else:
            # Pay late
            payment_date = (datetime.strptime(due_date, '%Y-%m-%d') + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        
        payment_id = f"PAY-{pay_counter:08d}"
        payment_number = generate_payment_number(pay_counter)
        pay_counter += 1
        
        # Full or partial payment
        if random.random() < 0.8:
            amount_paid = total_amount
        else:
            amount_paid = round(total_amount * random.uniform(0.5, 0.9), 2)
        
        payment_method = random.choice(['Wire Transfer', 'Credit Card', 'Check', 'ACH', 'Cash'])
        reference = f"REF-{random.randint(100000, 999999)}"
        
        payments.append((payment_id, payment_number, invoice_id, payment_date, amount_paid, payment_method, reference, None))
    
    cursor.executemany(
        "INSERT INTO fact_customer_payments (payment_id, payment_number, invoice_id, payment_date, amount_paid, payment_method, reference_number, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        payments
    )
    
    conn.commit()
    
    print(f"  Generated {len(leads)} CRM Leads")
    print(f"  Generated {len(quotations)} Sales Quotations")
    print(f"  Generated {len(sales_orders)} Sales Orders")
    print(f"  Generated {len(delivery_orders)} Delivery Orders")
    print(f"  Generated {len(invoices)} Customer Invoices")
    print(f"  Generated {len(payments)} Customer Payments")

# ========================================
# INVENTORY DEDUCTION FROM DELIVERIES
# ========================================

def process_delivery_inventory(conn):
    """Process delivery orders into inventory ledger (deductions)"""
    cursor = conn.cursor()
    
    print("Processing delivery inventory movements...")
    
    # Get all deliveries
    cursor.execute('''
        SELECT do.delivery_id, do.delivery_number, do.so_id, do.quantity_delivered, do.delivery_date,
               so.product_id, so.warehouse_id
        FROM fact_delivery_orders do
        JOIN fact_sales_orders so ON do.so_id = so.so_id
    ''')
    deliveries = cursor.fetchall()
    
    inventory_movements = []
    
    for delivery in deliveries:
        delivery_id, delivery_number, so_id, qty_delivered, date_str, product_id, warehouse_id = delivery
        
        inventory_movements.append((
            product_id, warehouse_id, date_str, 'DELIVERY', 'DELIVERY_ORDER', delivery_id,
            0, qty_delivered, None, None
        ))
    
    cursor.executemany(
        "INSERT INTO fact_inventory_ledger (product_id, warehouse_id, movement_date, movement_type, reference_type, reference_id, quantity_in, quantity_out, unit_cost, running_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        inventory_movements
    )
    
    conn.commit()
    print(f"  Processed {len(inventory_movements)} delivery inventory movements")
    
    # Recalculate running balances
    cursor.execute('''
        SELECT movement_id, product_id, warehouse_id, quantity_in, quantity_out
        FROM fact_inventory_ledger
        ORDER BY product_id, warehouse_id, movement_date, movement_id
    ''')
    movements = cursor.fetchall()
    
    balance_cache = {}
    updated_movements = []
    
    for m in movements:
        movement_id, product_id, warehouse_id, qty_in, qty_out = m
        key = (product_id, warehouse_id)
        
        current_balance = balance_cache.get(key, 0)
        new_balance = current_balance + qty_in - qty_out
        balance_cache[key] = new_balance
        
        updated_movements.append((new_balance, movement_id))
    
    cursor.executemany(
        "UPDATE fact_inventory_ledger SET running_balance = ? WHERE movement_id = ?",
        updated_movements
    )
    
    conn.commit()
    print("  Updated running balances")

# ========================================
# FIFO COSTING CALCULATION
# ========================================

def calculate_fifo_costs(conn):
    """Calculate cost of goods sold using FIFO method"""
    cursor = conn.cursor()
    
    print("Calculating FIFO costs for sales...")
    
    # Get all sales orders that have been delivered
    cursor.execute('''
        SELECT so.so_id, so.product_id, so.quantity, so.total_amount, so.order_date, so.warehouse_id
        FROM fact_sales_orders so
        WHERE so.status IN ('SHIPPED', 'DELIVERED')
    ''')
    sales_orders = cursor.fetchall()
    
    profitability_records = []
    
    for so in sales_orders:
        so_id, product_id, quantity, total_amount, order_date, warehouse_id = so
        
        revenue = total_amount
        
        # Get inventory lots for this product using FIFO
        cursor.execute('''
            SELECT unit_cost, running_balance
            FROM fact_inventory_ledger
            WHERE product_id = ? AND running_balance > 0 AND movement_type = 'GOODS_RECEIPT'
            ORDER BY movement_date, movement_id
        ''', (product_id,))
        
        lots = cursor.fetchall()
        
        if not lots:
            # No inventory - use estimated cost
            cost_rate = 0.6  # Assume 60% of selling price
            cogs = revenue * cost_rate
        else:
            # Calculate weighted average from available lots
            total_cost = 0
            total_qty = 0
            remaining_qty = quantity
            
            for unit_cost, balance in lots:
                if remaining_qty <= 0:
                    break
                qty_from_lot = min(remaining_qty, balance)
                total_cost += qty_from_lot * unit_cost
                total_qty += qty_from_lot
                remaining_qty -= qty_from_lot
            
            if total_qty > 0:
                cogs = total_cost
            else:
                cogs = revenue * 0.6  # Fallback
        
        gross_profit = revenue - cogs
        gross_margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
        
        profitability_records.append((
            so_id, product_id, quantity, revenue, cogs, gross_profit, round(gross_margin_pct, 2),
            order_date
        ))
    
    cursor.executemany(
        "INSERT INTO fact_sales_profitability (so_id, product_id, quantity_sold, revenue, cost_of_goods_sold, gross_profit, gross_margin_pct, calculation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        profitability_records
    )
    
    conn.commit()
    print(f"  Calculated profitability for {len(profitability_records)} sales orders")

# ========================================
# UPDATE CURRENT INVENTORY SNAPSHOT
# ========================================

def update_current_inventory(conn):
    """Update current inventory snapshot table"""
    cursor = conn.cursor()
    
    print("Updating current inventory snapshot...")
    
    cursor.execute("DELETE FROM fact_current_inventory")
    
    cursor.execute('''
        SELECT 
            product_id,
            warehouse_id,
            SUM(quantity_in) as total_in,
            SUM(quantity_out) as total_out,
            COUNT(DISTINCT movement_id) as movements
        FROM fact_inventory_ledger
        GROUP BY product_id, warehouse_id
        HAVING total_in > 0 OR total_out > 0
    ''')
    
    inventory_records = []
    
    for row in cursor.fetchall():
        product_id, warehouse_id, total_in, total_out, movements = row
        
        quantity_on_hand = total_in - total_out
        
        # Calculate average cost from receipts
        cursor.execute('''
            SELECT AVG(unit_cost) 
            FROM fact_inventory_ledger 
            WHERE product_id = ? AND warehouse_id = ? AND quantity_in > 0 AND unit_cost IS NOT NULL
        ''', (product_id, warehouse_id))
        
        avg_cost = cursor.fetchone()[0] or 0
        
        if quantity_on_hand > 0:
            inventory_records.append((
                product_id, warehouse_id, quantity_on_hand, round(avg_cost, 2),
                END_DATE.strftime('%Y-%m-%d')
            ))
    
    cursor.executemany(
        "INSERT INTO fact_current_inventory (product_id, warehouse_id, quantity_on_hand, average_cost, last_updated) VALUES (?, ?, ?, ?, ?)",
        inventory_records
    )
    
    conn.commit()
    print(f"  Updated {len(inventory_records)} inventory records")

# ========================================
# EXPORT TO CSV
# ========================================

def export_to_csv(conn):
    """Export all tables to CSV files"""
    print("Exporting data to CSV...")
    
    tables = [
        'dim_product', 'dim_supplier', 'dim_customer', 'dim_salesperson', 'dim_warehouse', 'dim_date',
        'fact_purchase_orders', 'fact_goods_receipts',
        'fact_crm_leads', 'fact_sales_quotations', 'fact_sales_orders', 
        'fact_delivery_orders', 'fact_customer_invoices', 'fact_customer_payments',
        'fact_inventory_ledger', 'fact_current_inventory', 'fact_sales_profitability'
    ]
    
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        csv_path = os.path.join(DATA_DIR, f"{table}.csv")
        df.to_csv(csv_path, index=False)
        print(f"  Exported {table}: {len(df)} rows")
    
    print("CSV export complete!")

# ========================================
# MAIN EXECUTION
# ========================================

def main():
    print("=" * 60)
    print("ERP Analytics Platform - Data Generation")
    print("=" * 60)
    print()
    
    # Setup database
    conn = setup_database()
    
    # Generate master data
    products, suppliers, customers, salespersons = generate_master_data(conn)
    
    # Generate Procure-to-Pay data
    goods_receipts = generate_procure_to_pay(conn, products, suppliers)
    
    # Process inventory from goods receipts
    process_inventory_movements(conn, goods_receipts)
    
    # Generate Order-to-Cash data
    generate_order_to_cash(conn, products, customers, salespersons)
    
    # Process inventory from deliveries
    process_delivery_inventory(conn)
    
    # Calculate FIFO costs
    calculate_fifo_costs(conn)
    
    # Update current inventory
    update_current_inventory(conn)
    
    # Export to CSV
    export_to_csv(conn)
    
    conn.close()
    
    print()
    print("=" * 60)
    print("Data generation complete!")
    print(f"Database: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()