"""
ERP Data Explorer - Flask Application
A professional interface for browsing, searching, filtering, and inspecting ERP data.
"""

import sqlite3
import os
from flask import Flask, render_template, request, jsonify, send_file
from contextlib import contextmanager
from datetime import datetime
import io
import csv

app = Flask(__name__)
# Use absolute path for PythonAnywhere
db_path = os.path.expanduser(os.environ.get('DATABASE_PATH', '~/AI-Projects/database/erp_database.db'))
app.config['DATABASE'] = db_path

# Add max/min to Jinja2 environment
from jinja2 import Environment
def max_func(*args):
    return max(*args)
def min_func(*args):
    return min(*args)
app.jinja_env.globals.update(max=max_func, min=min_func)

# Import and register Dashboard Blueprint
from dashboard_app import dashboard_bp
app.register_blueprint(dashboard_bp)

# Import and register AI Advisor Blueprint
from ai_advisor import ai_advisor_bp
app.register_blueprint(ai_advisor_bp)

# Add now variable to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# ========================================
# DATABASE CONNECTION
# ========================================

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

# ========================================
# HELPER FUNCTIONS
# ========================================

def get_table_columns(table_name):
    """Get column names for a table"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return columns

def get_table_count(table_name):
    """Get row count for a table"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0

def execute_query(query, params=None):
    """Execute a query and return results"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return columns, rows

# ========================================
# TABLE DEFINITIONS
# ========================================

TABLES = {
    'Master Data': [
        {'name': 'dim_product', 'display': 'Products', 'icon': '📦'},
        {'name': 'dim_customer', 'display': 'Customers', 'icon': '👥'},
        {'name': 'dim_supplier', 'display': 'Suppliers', 'icon': '🏭'},
        {'name': 'dim_salesperson', 'display': 'Salespersons', 'icon': '👔'},
        {'name': 'dim_warehouse', 'display': 'Warehouses', 'icon': '🏢'},
    ],
    'Transactions': [
        {'name': 'fact_purchase_orders', 'display': 'Purchase Orders', 'icon': '📋'},
        {'name': 'fact_goods_receipts', 'display': 'Goods Receipts', 'icon': '📥'},
        {'name': 'fact_sales_orders', 'display': 'Sales Orders', 'icon': '🛒'},
        {'name': 'fact_delivery_orders', 'display': 'Delivery Orders', 'icon': '🚚'},
        {'name': 'fact_customer_invoices', 'display': 'Invoices', 'icon': '📄'},
        {'name': 'fact_customer_payments', 'display': 'Payments', 'icon': '💳'},
        {'name': 'fact_inventory_ledger', 'display': 'Inventory Ledger', 'icon': '📊'},
        {'name': 'fact_sales_profitability', 'display': 'Profitability', 'icon': '💰'},
    ],
    'Analytics': [
        {'name': 'analytics_fact_sales', 'display': 'Sales Analytics', 'icon': '📈'},
        {'name': 'analytics_fact_purchases', 'display': 'Purchase Analytics', 'icon': '📉'},
        {'name': 'analytics_fact_inventory', 'display': 'Inventory Analytics', 'icon': '📦'},
        {'name': 'analytics_customer_performance', 'display': 'Customer Performance', 'icon': '⭐'},
        {'name': 'analytics_product_performance', 'display': 'Product Performance', 'icon': '🏆'},
        {'name': 'analytics_supplier_performance', 'display': 'Supplier Performance', 'icon': '🏅'},
        {'name': 'analytics_invoice_aging', 'display': 'Invoice Aging', 'icon': '⏰'},
        {'name': 'analytics_monthly_trends', 'display': 'Monthly Trends', 'icon': '📅'},
    ]
}

ALL_TABLES = [t['name'] for group in TABLES.values() for t in group]

# ========================================
# ROUTES
# ========================================

@app.route('/')
def index():
    """Home page with KPI cards"""
    kpis = []
    
    # Products
    products_count = get_table_count('dim_product')
    kpis.append({
        'title': 'Total Products',
        'value': f"{products_count:,}",
        'icon': '📦',
        'color': 'blue'
    })
    
    # Customers
    customers_count = get_table_count('dim_customer')
    kpis.append({
        'title': 'Total Customers',
        'value': f"{customers_count:,}",
        'icon': '👥',
        'color': 'green'
    })
    
    # Suppliers
    suppliers_count = get_table_count('dim_supplier')
    kpis.append({
        'title': 'Total Suppliers',
        'value': f"{suppliers_count:,}",
        'icon': '🏭',
        'color': 'purple'
    })
    
    # Sales Orders
    sales_orders_count = get_table_count('fact_sales_orders')
    kpis.append({
        'title': 'Total Sales Orders',
        'value': f"{sales_orders_count:,}",
        'icon': '🛒',
        'color': 'orange'
    })
    
    # Invoices
    invoices_count = get_table_count('fact_customer_invoices')
    kpis.append({
        'title': 'Total Invoices',
        'value': f"{invoices_count:,}",
        'icon': '📄',
        'color': 'red'
    })
    
    # Payments
    payments_count = get_table_count('fact_customer_payments')
    kpis.append({
        'title': 'Total Payments',
        'value': f"{payments_count:,}",
        'icon': '💳',
        'color': 'teal'
    })
    
    # Inventory Value
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(quantity_on_hand * average_cost) FROM fact_current_inventory")
            inventory_value = cursor.fetchone()[0] or 0
    except:
        inventory_value = 0
    
    kpis.append({
        'title': 'Total Inventory Value',
        'value': f"${inventory_value:,.2f}",
        'icon': '💰',
        'color': 'gold'
    })
    
    # Recent Activity
    recent_sales = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT so_number, order_date, total_amount, c.customer_name 
                FROM fact_sales_orders so 
                LEFT JOIN dim_customer c ON so.customer_id = c.customer_id 
                ORDER BY order_date DESC LIMIT 5
            """)
            recent_sales = [dict_from_row(row) for row in cursor.fetchall()]
    except:
        pass
    
    # Monthly Revenue Trend
    monthly_revenue = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT month_name || ' ' || CAST(year AS TEXT) as month, 
                       total_revenue, total_profit 
                FROM analytics_monthly_trends 
                ORDER BY year DESC, month DESC LIMIT 6
            """)
            monthly_revenue = [dict_from_row(row) for row in cursor.fetchall()]
    except:
        pass
    
    return render_template('index.html', kpis=kpis, recent_sales=recent_sales, 
                         monthly_revenue=monthly_revenue, tables=TABLES)

@app.route('/tables')
def tables():
    """Table Explorer page"""
    return render_template('tables.html', tables=TABLES)

@app.route('/table/<table_name>')
def table_view(table_name):
    """Browse a specific table with pagination, search, sort, filter"""
    if table_name not in ALL_TABLES:
        return render_template('error.html', message=f"Table '{table_name}' not found"), 404
    
    # Get table info
    columns = get_table_columns(table_name)
    total_count = get_table_count(table_name)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)  # Max 100 per page
    offset = (page - 1) * per_page
    
    # Search
    search = request.args.get('search', '')
    
    # Sort
    sort_col = request.args.get('sort', columns[0] if columns else '')
    sort_dir = request.args.get('dir', 'asc')
    
    # Build query
    where_clause = ""
    params = []
    
    if search:
        # Search in all text columns
        search_conditions = [f"{col} LIKE ?" for col in columns if col not in ['movement_id', 'profitability_id', 'id']]
        if search_conditions:
            where_clause = " WHERE " + " OR ".join(search_conditions)
            params = ['%' + search + '%'] * len(search_conditions)
    
    # Sort clause
    order_clause = ""
    if sort_col and sort_col in columns:
        sort_dir = 'desc' if sort_dir.lower() == 'desc' else 'asc'
        order_clause = f" ORDER BY {sort_col} {sort_dir.upper()}"
    
    # Get total filtered count
    if search:
        count_query = f"SELECT COUNT(*) FROM {table_name}{where_clause}"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(count_query, params)
            filtered_count = cursor.fetchone()[0]
    else:
        filtered_count = total_count
    
    # Get data
    query = f"SELECT * FROM {table_name}{where_clause}{order_clause} LIMIT {per_page} OFFSET {offset}"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = [dict_from_row(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        rows = []
    
    # Calculate pagination info
    total_pages = (filtered_count + per_page - 1) // per_page if filtered_count > 0 else 1
    
    # Find table display name
    table_display = table_name
    for group in TABLES.values():
        for t in group:
            if t['name'] == table_name:
                table_display = t['display']
                break
    
    return render_template('table_view.html', 
                         table_name=table_name,
                         table_display=table_display,
                         columns=columns,
                         rows=rows,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_count=total_count,
                         filtered_count=filtered_count,
                         search=search,
                         sort_col=sort_col,
                         sort_dir=sort_dir,
                         tables=TABLES)

@app.route('/export/<table_name>')
def export_table(table_name):
    """Export table data to CSV"""
    if table_name not in ALL_TABLES:
        return jsonify({'error': 'Table not found'}), 404
    
    # Get optional filters from query params
    search = request.args.get('search', '')
    
    # Build query
    where_clause = ""
    params = []
    
    if search:
        columns = get_table_columns(table_name)
        search_conditions = [f"{col} LIKE ?" for col in columns if col not in ['movement_id', 'profitability_id', 'id']]
        if search_conditions:
            where_clause = " WHERE " + " OR ".join(search_conditions)
            params = ['%' + search + '%'] * len(search_conditions)
    
    query = f"SELECT * FROM {table_name}{where_clause}"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table_name}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================
# DETAIL PAGES
# ========================================

@app.route('/customer/<customer_id>')
def customer_detail(customer_id):
    """Customer detail page"""
    # Get customer info
    customer = None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dim_customer WHERE customer_id = ?", (customer_id,))
        row = cursor.fetchone()
        if row:
            customer = dict_from_row(row)
    
    if not customer:
        return render_template('error.html', message=f"Customer '{customer_id}' not found"), 404
    
    # Sales Orders
    sales_orders = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT so.*, p.product_name 
            FROM fact_sales_orders so 
            LEFT JOIN dim_product p ON so.product_id = p.product_id 
            WHERE so.customer_id = ? 
            ORDER BY so.order_date DESC LIMIT 50
        """, (customer_id,))
        sales_orders = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Invoices
    invoices = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.*, so.so_number 
            FROM fact_customer_invoices ci 
            LEFT JOIN fact_sales_orders so ON ci.so_id = so.so_id 
            WHERE so.customer_id = ? 
            ORDER BY ci.invoice_date DESC LIMIT 50
        """, (customer_id,))
        invoices = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Payments
    payments = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cp.*, ci.invoice_number, ci.total_amount 
            FROM fact_customer_payments cp 
            LEFT JOIN fact_customer_invoices ci ON cp.invoice_id = ci.invoice_id
            LEFT JOIN fact_sales_orders so ON ci.so_id = so.so_id
            WHERE so.customer_id = ?
            ORDER BY cp.payment_date DESC LIMIT 50
        """, (customer_id,))
        payments = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Profitability Summary
    profit_summary = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as orders, 
                   SUM(revenue) as revenue, 
                   SUM(gross_profit) as profit,
                   AVG(gross_margin_pct) as margin
            FROM fact_sales_profitability spf
            JOIN fact_sales_orders so ON spf.so_id = so.so_id
            WHERE so.customer_id = ?
        """, (customer_id,))
        row = cursor.fetchone()
        if row:
            profit_summary = dict_from_row(row)
    
    return render_template('customer_detail.html', customer=customer,
                         sales_orders=sales_orders, invoices=invoices,
                         payments=payments, profit_summary=profit_summary, tables=TABLES)

@app.route('/supplier/<supplier_id>')
def supplier_detail(supplier_id):
    """Supplier detail page"""
    # Get supplier info
    supplier = None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dim_supplier WHERE supplier_id = ?", (supplier_id,))
        row = cursor.fetchone()
        if row:
            supplier = dict_from_row(row)
    
    if not supplier:
        return render_template('error.html', message=f"Supplier '{supplier_id}' not found"), 404
    
    # Purchase Orders
    purchase_orders = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT po.*, p.product_name 
            FROM fact_purchase_orders po 
            LEFT JOIN dim_product p ON po.product_id = p.product_id 
            WHERE po.supplier_id = ? 
            ORDER BY po.order_date DESC LIMIT 50
        """, (supplier_id,))
        purchase_orders = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Goods Receipts
    goods_receipts = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT gr.*, po.product_id, po.unit_cost, w.warehouse_name
            FROM fact_goods_receipts gr 
            LEFT JOIN fact_purchase_orders po ON gr.po_id = po.po_id
            LEFT JOIN dim_warehouse w ON gr.warehouse_id = w.warehouse_id
            WHERE po.supplier_id = ?
            ORDER BY gr.receipt_date DESC LIMIT 50
        """, (supplier_id,))
        goods_receipts = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Spend Analysis
    spend_summary = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as orders, 
                   SUM(total_cost) as total_spend,
                   AVG(unit_cost) as avg_cost,
                   SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed
            FROM fact_purchase_orders 
            WHERE supplier_id = ?
        """, (supplier_id,))
        row = cursor.fetchone()
        if row:
            spend_summary = dict_from_row(row)
    
    return render_template('supplier_detail.html', supplier=supplier,
                         purchase_orders=purchase_orders, goods_receipts=goods_receipts,
                         spend_summary=spend_summary, tables=TABLES)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    # Get product info
    product = None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dim_product WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        if row:
            product = dict_from_row(row)
    
    if not product:
        return render_template('error.html', message=f"Product '{product_id}' not found"), 404
    
    # Purchase History
    purchase_history = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT po.order_date, po.quantity, po.unit_cost, po.total_cost, s.supplier_name
            FROM fact_purchase_orders po
            LEFT JOIN dim_supplier s ON po.supplier_id = s.supplier_id
            WHERE po.product_id = ?
            ORDER BY po.order_date DESC LIMIT 50
        """, (product_id,))
        purchase_history = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Sales History
    sales_history = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT so.order_date, so.quantity, so.unit_price, so.total_amount, c.customer_name
            FROM fact_sales_orders so
            LEFT JOIN dim_customer c ON so.customer_id = c.customer_id
            WHERE so.product_id = ?
            ORDER BY so.order_date DESC LIMIT 50
        """, (product_id,))
        sales_history = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Inventory Movements
    inventory_movements = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT movement_date, movement_type, quantity_in, quantity_out, 
                   running_balance, unit_cost, warehouse_id
            FROM fact_inventory_ledger
            WHERE product_id = ?
            ORDER BY movement_date DESC LIMIT 50
        """, (product_id,))
        inventory_movements = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Margin Analysis
    margin_summary = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as transactions,
                   SUM(quantity_sold) as units_sold,
                   SUM(revenue) as total_revenue,
                   SUM(cost_of_goods_sold) as total_cost,
                   SUM(gross_profit) as total_profit,
                   AVG(gross_margin_pct) as avg_margin
            FROM fact_sales_profitability
            WHERE product_id = ?
        """, (product_id,))
        row = cursor.fetchone()
        if row:
            margin_summary = dict_from_row(row)
    
    # Current Inventory
    current_inventory = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.*, w.warehouse_name
            FROM fact_current_inventory ci
            LEFT JOIN dim_warehouse w ON ci.warehouse_id = w.warehouse_id
            WHERE ci.product_id = ?
        """, (product_id,))
        current_inventory = [dict_from_row(row) for row in cursor.fetchall()]
    
    return render_template('product_detail.html', product=product,
                         purchase_history=purchase_history, sales_history=sales_history,
                         inventory_movements=inventory_movements, margin_summary=margin_summary,
                         current_inventory=current_inventory, tables=TABLES)

# ========================================
# DATA QUALITY DASHBOARD
# ========================================

@app.route('/data-quality')
def data_quality():
    """Data Quality Dashboard"""
    issues = []
    total_issues = 0
    
    # 1. Negative Inventory
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM fact_inventory_ledger 
                WHERE running_balance < 0
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append({
                    'type': 'negative_inventory',
                    'title': 'Negative Inventory',
                    'description': 'Records with negative running balance',
                    'count': count,
                    'severity': 'high'
                })
                total_issues += count
    except:
        pass
    
    # 2. Missing Foreign Keys (Sales Orders without Customer)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM fact_sales_orders so
                LEFT JOIN dim_customer c ON so.customer_id = c.customer_id
                WHERE c.customer_id IS NULL
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append({
                    'type': 'missing_customer_fk',
                    'title': 'Missing Customer Reference',
                    'description': 'Sales orders with invalid customer reference',
                    'count': count,
                    'severity': 'high'
                })
                total_issues += count
    except:
        pass
    
    # 3. Missing Foreign Keys (Purchase Orders without Supplier)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM fact_purchase_orders po
                LEFT JOIN dim_supplier s ON po.supplier_id = s.supplier_id
                WHERE s.supplier_id IS NULL
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append({
                    'type': 'missing_supplier_fk',
                    'title': 'Missing Supplier Reference',
                    'description': 'Purchase orders with invalid supplier reference',
                    'count': count,
                    'severity': 'high'
                })
                total_issues += count
    except:
        pass
    
    # 4. Duplicate Records (Products with same SKU)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sku, COUNT(*) as count 
                FROM dim_product 
                GROUP BY sku 
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            count = sum(row[1] for row in duplicates)
            if count > 0:
                issues.append({
                    'type': 'duplicate_skus',
                    'title': 'Duplicate SKU',
                    'description': 'Products with duplicate SKU codes',
                    'count': count,
                    'severity': 'medium'
                })
                total_issues += count
    except:
        pass
    
    # 5. Unpaid Invoices
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(total_amount) as total
                FROM fact_customer_invoices
                WHERE status = 'OPEN' AND amount_paid = 0
            """)
            row = cursor.fetchone()
            if row[0] > 0:
                issues.append({
                    'type': 'unpaid_invoices',
                    'title': 'Unpaid Invoices',
                    'description': f"Open invoices with zero payment (${row[1] or 0:,.2f} total)",
                    'count': row[0],
                    'severity': 'medium'
                })
                total_issues += row[0]
    except:
        pass
    
    # 6. Overdue Invoices
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(total_amount - amount_paid) as total
                FROM fact_customer_invoices
                WHERE status = 'OVERDUE'
            """)
            row = cursor.fetchone()
            if row[0] > 0:
                issues.append({
                    'type': 'overdue_invoices',
                    'title': 'Overdue Invoices',
                    'description': f"Invoices past due date (${row[1] or 0:,.2f} outstanding)",
                    'count': row[0],
                    'severity': 'high'
                })
                total_issues += row[0]
    except:
        pass
    
    # 7. Inventory Anomalies (Zero cost receipts)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM fact_inventory_ledger
                WHERE quantity_in > 0 AND (unit_cost IS NULL OR unit_cost = 0)
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append({
                    'type': 'zero_cost_receipts',
                    'title': 'Zero Cost Receipts',
                    'description': 'Goods receipts with no or zero unit cost',
                    'count': count,
                    'severity': 'medium'
                })
                total_issues += count
    except:
        pass
    
    # 8. Cancelled Orders with Deliveries
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM fact_delivery_orders do
                JOIN fact_sales_orders so ON do.so_id = so.so_id
                WHERE so.status = 'CANCELLED'
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                issues.append({
                    'type': 'cancelled_deliveries',
                    'title': 'Cancelled Order Deliveries',
                    'description': 'Deliveries made for cancelled orders',
                    'count': count,
                    'severity': 'low'
                })
                total_issues += count
    except:
        pass
    
    # Data Quality Score
    total_records = sum(get_table_count(t) for t in ALL_TABLES)
    quality_score = max(0, 100 - (total_issues / max(total_records, 1) * 10))
    
    return render_template('data_quality.html', issues=issues, 
                         total_issues=total_issues, quality_score=quality_score,
                         tables=TABLES)

# ========================================
# LIST PAGES
# ========================================

@app.route('/customers')
def customer_list():
    """Customer list page with search"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    if search:
        query = "SELECT customer_id, customer_name, industry, region FROM dim_customer WHERE customer_name LIKE ? OR customer_id LIKE ? LIMIT ? OFFSET ?"
        params = [f'%{search}%', f'%{search}%', per_page, (page-1)*per_page]
        count_query = "SELECT COUNT(*) FROM dim_customer WHERE customer_name LIKE ? OR customer_id LIKE ?"
        count_params = [f'%{search}%', f'%{search}%']
    else:
        query = "SELECT customer_id, customer_name, industry, region FROM dim_customer ORDER BY customer_name LIMIT ? OFFSET ?"
        params = [per_page, (page-1)*per_page]
        count_query = "SELECT COUNT(*) FROM dim_customer"
        count_params = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        customers = [dict_from_row(row) for row in cursor.fetchall()]
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return render_template('customer_list.html', customers=customers, 
                         search=search, page=page, total_pages=total_pages,
                         total=total, tables=TABLES)

@app.route('/suppliers')
def supplier_list():
    """Supplier list page with search"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    if search:
        query = "SELECT supplier_id, supplier_name, country, supplier_type FROM dim_supplier WHERE supplier_name LIKE ? OR supplier_id LIKE ? LIMIT ? OFFSET ?"
        params = [f'%{search}%', f'%{search}%', per_page, (page-1)*per_page]
        count_query = "SELECT COUNT(*) FROM dim_supplier WHERE supplier_name LIKE ? OR supplier_id LIKE ?"
        count_params = [f'%{search}%', f'%{search}%']
    else:
        query = "SELECT supplier_id, supplier_name, country, supplier_type FROM dim_supplier ORDER BY supplier_name LIMIT ? OFFSET ?"
        params = [per_page, (page-1)*per_page]
        count_query = "SELECT COUNT(*) FROM dim_supplier"
        count_params = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        suppliers = [dict_from_row(row) for row in cursor.fetchall()]
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return render_template('supplier_list.html', suppliers=suppliers,
                         search=search, page=page, total_pages=total_pages,
                         total=total, tables=TABLES)

@app.route('/products')
def product_list():
    """Product list page with search"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    if search:
        query = "SELECT product_id, product_name, sku, category, default_selling_price FROM dim_product WHERE product_name LIKE ? OR sku LIKE ? OR product_id LIKE ? LIMIT ? OFFSET ?"
        params = [f'%{search}%', f'%{search}%', f'%{search}%', per_page, (page-1)*per_page]
        count_query = "SELECT COUNT(*) FROM dim_product WHERE product_name LIKE ? OR sku LIKE ? OR product_id LIKE ?"
        count_params = [f'%{search}%', f'%{search}%', f'%{search}%']
    else:
        query = "SELECT product_id, product_name, sku, category, default_selling_price FROM dim_product ORDER BY product_name LIMIT ? OFFSET ?"
        params = [per_page, (page-1)*per_page]
        count_query = "SELECT COUNT(*) FROM dim_product"
        count_params = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        products = [dict_from_row(row) for row in cursor.fetchall()]
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return render_template('product_list.html', products=products,
                         search=search, page=page, total_pages=total_pages,
                         total=total, tables=TABLES)

# ========================================
# SQL QUERY PAGE
# ========================================

@app.route('/sql-query')
def sql_query():
    """SQL Query page"""
    return render_template('sql_query.html', tables=TABLES, table_list=ALL_TABLES)

@app.route('/execute-sql', methods=['POST'])
def execute_sql():
    """Execute a SQL query (read-only)"""
    sql = request.form.get('sql', '').strip()
    
    if not sql:
        return jsonify({'error': 'No query provided', 'columns': [], 'rows': []}), 400
    
    # Validate query is SELECT only
    sql_upper = sql.upper()
    
    # Block dangerous operations
    forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
    for cmd in forbidden:
        if cmd in sql_upper:
            return jsonify({
                'error': f"Operation {cmd} is not allowed. Only SELECT queries are permitted.",
                'columns': [],
                'rows': []
            }), 500
    
    # Must start with SELECT
    if not sql_upper.strip().startswith('SELECT'):
        return jsonify({
            'error': 'Only SELECT queries are allowed.',
            'columns': [],
            'rows': []
        }), 500
    
    # Block multiple statements (basic check)
    if ';' in sql.rstrip(';').replace("';", ""):
        return jsonify({
            'error': 'Multiple statements are not allowed.',
            'columns': [],
            'rows': []
        }), 500
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = [list(row) for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'columns': columns,
                'rows': rows,
                'row_count': len(rows)
            })
    except sqlite3.Error as e:
        return jsonify({
            'error': str(e),
            'columns': [],
            'rows': []
        }), 500

# ========================================
# API ENDPOINTS
# ========================================

@app.route('/api/tables')
def api_tables():
    """Get list of all tables with counts"""
    result = []
    for group_name, tables_list in TABLES.items():
        for t in tables_list:
            result.append({
                'name': t['name'],
                'display': t['display'],
                'group': group_name,
                'icon': t['icon'],
                'count': get_table_count(t['name'])
            })
    return jsonify(result)

@app.route('/api/schema/<table_name>')
def api_schema(table_name):
    """Get table schema"""
    if table_name not in ALL_TABLES:
        return jsonify({'error': 'Table not found'}), 404
    
    columns = get_table_columns(table_name)
    return jsonify({
        'table': table_name,
        'columns': columns
    })

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found', tables=TABLES), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error', tables=TABLES), 500

# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)