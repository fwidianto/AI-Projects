"""
ERP Analytics Platform - ETL Pipeline
Transforms raw transactional data into analytics-ready tables
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DB_PATH = os.path.join(DATABASE_DIR, 'erp_database.db')

def connect_db():
    return sqlite3.connect(DB_PATH)

# ========================================
# ANALYTICS TABLES
# ========================================

def create_analytics_tables(conn):
    """Create analytics-ready tables"""
    cursor = conn.cursor()
    
    print("Creating analytics tables...")
    
    # ========================================
    # Fact Sales Summary (Aggregated Sales)
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_fact_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            so_id TEXT,
            so_number TEXT,
            order_date DATE,
            year INTEGER,
            month INTEGER,
            quarter INTEGER,
            fiscal_year INTEGER,
            customer_id TEXT,
            customer_name TEXT,
            industry TEXT,
            region TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            salesperson_id TEXT,
            salesperson_name TEXT,
            warehouse_id TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_revenue REAL,
            cost_of_goods_sold REAL,
            gross_profit REAL,
            gross_margin_pct REAL,
            days_to_deliver INTEGER,
            FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
        )
    ''')
    
    # ========================================
    # Fact Purchases Summary
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_fact_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id TEXT,
            po_number TEXT,
            order_date DATE,
            year INTEGER,
            month INTEGER,
            quarter INTEGER,
            supplier_id TEXT,
            supplier_name TEXT,
            country TEXT,
            supplier_type TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit_cost REAL,
            total_cost REAL,
            receipt_date DATE,
            days_to_deliver INTEGER,
            on_time_delivery INTEGER,
            status TEXT
        )
    ''')
    
    # ========================================
    # Fact Inventory Summary
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_fact_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            product_name TEXT,
            sku TEXT,
            category TEXT,
            warehouse_id TEXT,
            warehouse_name TEXT,
            quantity_on_hand INTEGER,
            average_cost REAL,
            total_value REAL,
            last_receipt_date DATE,
            days_since_last_receipt INTEGER,
            turns_per_year REAL,
            last_updated DATE
        )
    ''')
    
    # ========================================
    # Customer Analytics
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_customer_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            customer_name TEXT,
            industry TEXT,
            region TEXT,
            total_orders INTEGER,
            total_revenue REAL,
            total_profit REAL,
            avg_margin_pct REAL,
            total_invoices INTEGER,
            open_invoices INTEGER,
            overdue_invoices INTEGER,
            avg_days_to_pay INTEGER,
            last_order_date DATE
        )
    ''')
    
    # ========================================
    # Product Analytics
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_product_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            product_name TEXT,
            sku TEXT,
            category TEXT,
            units_sold INTEGER,
            total_revenue REAL,
            total_profit REAL,
            avg_margin_pct REAL,
            total_purchases INTEGER,
            avg_cost REAL,
            current_inventory INTEGER
        )
    ''')
    
    # ========================================
    # Supplier Analytics
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_supplier_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT,
            supplier_name TEXT,
            country TEXT,
            supplier_type TEXT,
            total_orders INTEGER,
            total_spend REAL,
            on_time_rate REAL,
            avg_lead_time_days REAL,
            product_variety INTEGER
        )
    ''')
    
    # ========================================
    # Salesperson Analytics
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_salesperson_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salesperson_id TEXT,
            salesperson_name TEXT,
            region TEXT,
            total_leads INTEGER,
            converted_leads INTEGER,
            conversion_rate REAL,
            total_orders INTEGER,
            total_revenue REAL,
            avg_order_value REAL,
            total_profit REAL,
            avg_margin_pct REAL
        )
    ''')
    
    # ========================================
    # Invoice Aging
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_invoice_aging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            invoice_number TEXT,
            so_number TEXT,
            invoice_date DATE,
            due_date DATE,
            customer_id TEXT,
            customer_name TEXT,
            total_amount REAL,
            amount_paid REAL,
            amount_outstanding REAL,
            days_overdue INTEGER,
            aging_bucket TEXT,
            status TEXT
        )
    ''')
    
    # ========================================
    # Monthly Trend Summary
    # ========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_monthly_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month INTEGER,
            month_name TEXT,
            fiscal_year INTEGER,
            fiscal_quarter INTEGER,
            total_sales_orders INTEGER,
            total_revenue REAL,
            total_cost REAL,
            total_profit REAL,
            avg_margin_pct REAL,
            total_customers INTEGER,
            total_products_sold INTEGER,
            total_purchase_orders INTEGER,
            total_purchase_spend REAL,
            inventory_value REAL
        )
    ''')
    
    conn.commit()
    print("  Analytics tables created successfully!")

def load_fact_sales(conn):
    """Load fact sales analytics"""
    cursor = conn.cursor()
    
    print("Loading Fact Sales...")
    
    cursor.execute("DELETE FROM analytics_fact_sales")
    
    cursor.execute('''
        INSERT INTO analytics_fact_sales (
            so_id, so_number, order_date, year, month, quarter, fiscal_year,
            customer_id, customer_name, industry, region,
            product_id, product_name, category,
            salesperson_id, salesperson_name, warehouse_id,
            quantity, unit_price, total_revenue,
            cost_of_goods_sold, gross_profit, gross_margin_pct, days_to_deliver
        )
        SELECT 
            so.so_id,
            so.so_number,
            so.order_date,
            CAST(strftime('%Y', so.order_date) AS INTEGER) as year,
            CAST(strftime('%m', so.order_date) AS INTEGER) as month,
            CAST(strftime('%m', so.order_date) AS INTEGER) / 3 + 1 as quarter,
            CASE WHEN CAST(strftime('%m', so.order_date) AS INTEGER) >= 7 
                 THEN CAST(strftime('%Y', so.order_date) AS INTEGER)
                 ELSE CAST(strftime('%Y', so.order_date) AS INTEGER) - 1 END as fiscal_year,
            c.customer_id,
            c.customer_name,
            c.industry,
            c.region,
            p.product_id,
            p.product_name,
            p.category,
            sp.salesperson_id,
            sp.first_name || ' ' || sp.last_name as salesperson_name,
            so.warehouse_id,
            so.quantity,
            so.unit_price,
            so.total_amount as total_revenue,
            COALESCE(spf.cost_of_goods_sold, so.total_amount * 0.6) as cost_of_goods_sold,
            COALESCE(spf.gross_profit, so.total_amount * 0.4) as gross_profit,
            COALESCE(spf.gross_margin_pct, 40) as gross_margin_pct,
            CASE WHEN so.actual_delivery_date IS NOT NULL 
                 THEN julianday(so.actual_delivery_date) - julianday(so.order_date)
                 ELSE NULL END as days_to_deliver
        FROM fact_sales_orders so
        JOIN dim_customer c ON so.customer_id = c.customer_id
        JOIN dim_product p ON so.product_id = p.product_id
        LEFT JOIN dim_salesperson sp ON so.salesperson_id = sp.salesperson_id
        LEFT JOIN fact_sales_profitability spf ON so.so_id = spf.so_id
        WHERE so.status != 'CANCELLED'
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} sales records")

def load_fact_purchases(conn):
    """Load fact purchases analytics"""
    cursor = conn.cursor()
    
    print("Loading Fact Purchases...")
    
    cursor.execute("DELETE FROM analytics_fact_purchases")
    
    cursor.execute('''
        INSERT INTO analytics_fact_purchases (
            po_id, po_number, order_date, year, month, quarter,
            supplier_id, supplier_name, country, supplier_type,
            product_id, product_name, category,
            quantity, unit_cost, total_cost,
            receipt_date, days_to_deliver, on_time_delivery, status
        )
        SELECT 
            po.po_id,
            po.po_number,
            po.order_date,
            CAST(strftime('%Y', po.order_date) AS INTEGER) as year,
            CAST(strftime('%m', po.order_date) AS INTEGER) as month,
            CAST(strftime('%m', po.order_date) AS INTEGER) / 3 + 1 as quarter,
            s.supplier_id,
            s.supplier_name,
            s.country,
            s.supplier_type,
            p.product_id,
            p.product_name,
            p.category,
            po.quantity,
            po.unit_cost,
            po.total_cost,
            po.actual_receipt_date as receipt_date,
            CASE WHEN po.actual_receipt_date IS NOT NULL AND po.expected_receipt_date IS NOT NULL
                 THEN julianday(po.actual_receipt_date) - julianday(po.order_date)
                 ELSE NULL END as days_to_deliver,
            CASE WHEN po.actual_receipt_date IS NOT NULL AND po.expected_receipt_date IS NOT NULL
                 THEN CASE WHEN julianday(po.actual_receipt_date) <= julianday(po.expected_receipt_date) THEN 1 ELSE 0 END
                 ELSE NULL END as on_time_delivery,
            po.status
        FROM fact_purchase_orders po
        JOIN dim_supplier s ON po.supplier_id = s.supplier_id
        JOIN dim_product p ON po.product_id = p.product_id
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} purchase records")

def load_fact_inventory(conn):
    """Load fact inventory analytics"""
    cursor = conn.cursor()
    
    print("Loading Fact Inventory...")
    
    cursor.execute("DELETE FROM analytics_fact_inventory")
    
    cursor.execute('''
        INSERT INTO analytics_fact_inventory (
            product_id, product_name, sku, category,
            warehouse_id, warehouse_name,
            quantity_on_hand, average_cost, total_value,
            last_receipt_date, days_since_last_receipt,
            turns_per_year, last_updated
        )
        SELECT 
            ci.product_id,
            p.product_name,
            p.sku,
            p.category,
            ci.warehouse_id,
            w.warehouse_name,
            ci.quantity_on_hand,
            ci.average_cost,
            ci.quantity_on_hand * ci.average_cost as total_value,
            (SELECT MAX(receipt_date) FROM fact_goods_receipts gr 
             JOIN fact_purchase_orders po ON gr.po_id = po.po_id 
             WHERE po.product_id = ci.product_id) as last_receipt_date,
            CASE WHEN (SELECT MAX(receipt_date) FROM fact_goods_receipts gr 
                       JOIN fact_purchase_orders po ON gr.po_id = po.po_id 
                       WHERE po.product_id = ci.product_id) IS NOT NULL
                 THEN julianday('now') - julianday((SELECT MAX(receipt_date) FROM fact_goods_receipts gr 
                                                    JOIN fact_purchase_orders po ON gr.po_id = po.po_id 
                                                    WHERE po.product_id = ci.product_id))
                 ELSE NULL END as days_since_last_receipt,
            NULL as turns_per_year,
            ci.last_updated
        FROM fact_current_inventory ci
        JOIN dim_product p ON ci.product_id = p.product_id
        JOIN dim_warehouse w ON ci.warehouse_id = w.warehouse_id
        WHERE ci.quantity_on_hand > 0
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} inventory records")

def load_customer_analytics(conn):
    """Load customer performance analytics"""
    cursor = conn.cursor()
    
    print("Loading Customer Analytics...")
    
    cursor.execute("DELETE FROM analytics_customer_performance")
    
    cursor.execute('''
        INSERT INTO analytics_customer_performance (
            customer_id, customer_name, industry, region,
            total_orders, total_revenue, total_profit, avg_margin_pct,
            total_invoices, open_invoices, overdue_invoices,
            avg_days_to_pay, last_order_date
        )
        SELECT 
            c.customer_id,
            c.customer_name,
            c.industry,
            c.region,
            COUNT(DISTINCT so.so_id) as total_orders,
            COALESCE(SUM(so.total_amount), 0) as total_revenue,
            COALESCE(SUM(spf.gross_profit), SUM(so.total_amount) * 0.4) as total_profit,
            COALESCE(AVG(spf.gross_margin_pct), 40) as avg_margin_pct,
            COUNT(DISTINCT ci.invoice_id) as total_invoices,
            SUM(CASE WHEN ci.status = 'OPEN' THEN 1 ELSE 0 END) as open_invoices,
            SUM(CASE WHEN ci.status = 'OVERDUE' THEN 1 ELSE 0 END) as overdue_invoices,
            COALESCE(AVG(
                (SELECT julianday(MAX(cp.payment_date)) - julianday(ci.invoice_date)
                 FROM fact_customer_payments cp WHERE cp.invoice_id = ci.invoice_id)
            ), 0) as avg_days_to_pay,
            MAX(so.order_date) as last_order_date
        FROM dim_customer c
        LEFT JOIN fact_sales_orders so ON c.customer_id = so.customer_id AND so.status != 'CANCELLED'
        LEFT JOIN fact_sales_profitability spf ON so.so_id = spf.so_id
        LEFT JOIN fact_customer_invoices ci ON so.so_id = ci.so_id
        GROUP BY c.customer_id
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} customer records")

def load_product_analytics(conn):
    """Load product performance analytics"""
    cursor = conn.cursor()
    
    print("Loading Product Analytics...")
    
    cursor.execute("DELETE FROM analytics_product_performance")
    
    cursor.execute('''
        INSERT INTO analytics_product_performance (
            product_id, product_name, sku, category,
            units_sold, total_revenue, total_profit, avg_margin_pct,
            total_purchases, avg_cost, current_inventory
        )
        SELECT 
            p.product_id,
            p.product_name,
            p.sku,
            p.category,
            COALESCE(SUM(so.quantity), 0) as units_sold,
            COALESCE(SUM(so.total_amount), 0) as total_revenue,
            COALESCE(SUM(spf.gross_profit), SUM(so.total_amount) * 0.4) as total_profit,
            COALESCE(AVG(spf.gross_margin_pct), 40) as avg_margin_pct,
            COUNT(DISTINCT po.po_id) as total_purchases,
            COALESCE(AVG(po.unit_cost), p.default_selling_price * 0.6) as avg_cost,
            COALESCE((SELECT SUM(quantity_on_hand) FROM fact_current_inventory WHERE product_id = p.product_id), 0) as current_inventory
        FROM dim_product p
        LEFT JOIN fact_sales_orders so ON p.product_id = so.product_id AND so.status != 'CANCELLED'
        LEFT JOIN fact_sales_profitability spf ON p.product_id = spf.product_id
        LEFT JOIN fact_purchase_orders po ON p.product_id = po.product_id
        GROUP BY p.product_id
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} product records")

def load_supplier_analytics(conn):
    """Load supplier performance analytics"""
    cursor = conn.cursor()
    
    print("Loading Supplier Analytics...")
    
    cursor.execute("DELETE FROM analytics_supplier_performance")
    
    cursor.execute('''
        INSERT INTO analytics_supplier_performance (
            supplier_id, supplier_name, country, supplier_type,
            total_orders, total_spend, on_time_rate, avg_lead_time_days, product_variety
        )
        SELECT 
            s.supplier_id,
            s.supplier_name,
            s.country,
            s.supplier_type,
            COUNT(DISTINCT po.po_id) as total_orders,
            COALESCE(SUM(po.total_cost), 0) as total_spend,
            COALESCE(AVG(
                CASE WHEN po.actual_receipt_date IS NOT NULL AND po.expected_receipt_date IS NOT NULL
                     THEN CASE WHEN julianday(po.actual_receipt_date) <= julianday(po.expected_receipt_date) THEN 1.0 ELSE 0.0 END
                     ELSE NULL END
            ), 0) as on_time_rate,
            COALESCE(AVG(
                CASE WHEN po.actual_receipt_date IS NOT NULL
                     THEN julianday(po.actual_receipt_date) - julianday(po.order_date)
                     ELSE NULL END
            ), 0) as avg_lead_time_days,
            COUNT(DISTINCT po.product_id) as product_variety
        FROM dim_supplier s
        LEFT JOIN fact_purchase_orders po ON s.supplier_id = po.supplier_id
        GROUP BY s.supplier_id
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} supplier records")

def load_salesperson_analytics(conn):
    """Load salesperson performance analytics"""
    cursor = conn.cursor()
    
    print("Loading Salesperson Analytics...")
    
    cursor.execute("DELETE FROM analytics_salesperson_performance")
    
    cursor.execute('''
        INSERT INTO analytics_salesperson_performance (
            salesperson_id, salesperson_name, region,
            total_leads, converted_leads, conversion_rate,
            total_orders, total_revenue, avg_order_value,
            total_profit, avg_margin_pct
        )
        SELECT 
            sp.salesperson_id,
            sp.first_name || ' ' || sp.last_name as salesperson_name,
            sp.region,
            COUNT(DISTINCT l.lead_id) as total_leads,
            SUM(CASE WHEN l.lead_status = 'CONVERTED' THEN 1 ELSE 0 END) as converted_leads,
            CASE WHEN COUNT(DISTINCT l.lead_id) > 0 
                 THEN CAST(SUM(CASE WHEN l.lead_status = 'CONVERTED' THEN 1 ELSE 0 END) AS REAL) / COUNT(DISTINCT l.lead_id) * 100
                 ELSE 0 END as conversion_rate,
            COUNT(DISTINCT so.so_id) as total_orders,
            COALESCE(SUM(so.total_amount), 0) as total_revenue,
            CASE WHEN COUNT(DISTINCT so.so_id) > 0 
                 THEN COALESCE(SUM(so.total_amount), 0) / COUNT(DISTINCT so.so_id)
                 ELSE 0 END as avg_order_value,
            COALESCE(SUM(spf.gross_profit), SUM(so.total_amount) * 0.4) as total_profit,
            COALESCE(AVG(spf.gross_margin_pct), 40) as avg_margin_pct
        FROM dim_salesperson sp
        LEFT JOIN fact_crm_leads l ON sp.salesperson_id = l.salesperson_id
        LEFT JOIN fact_sales_orders so ON sp.salesperson_id = so.salesperson_id AND so.status != 'CANCELLED'
        LEFT JOIN fact_sales_profitability spf ON so.so_id = spf.so_id
        GROUP BY sp.salesperson_id
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} salesperson records")

def load_invoice_aging(conn):
    """Load invoice aging analytics"""
    cursor = conn.cursor()
    
    print("Loading Invoice Aging...")
    
    cursor.execute("DELETE FROM analytics_invoice_aging")
    
    cursor.execute('''
        INSERT INTO analytics_invoice_aging (
            invoice_id, invoice_number, so_number,
            invoice_date, due_date,
            customer_id, customer_name,
            total_amount, amount_paid, amount_outstanding,
            days_overdue, aging_bucket, status
        )
        SELECT 
            ci.invoice_id,
            ci.invoice_number,
            so.so_number,
            ci.invoice_date,
            ci.due_date,
            c.customer_id,
            c.customer_name,
            ci.total_amount,
            ci.amount_paid,
            ci.total_amount - ci.amount_paid as amount_outstanding,
            CASE WHEN ci.due_date < date('now') AND ci.status != 'PAID'
                 THEN julianday('now') - julianday(ci.due_date)
                 ELSE 0 END as days_overdue,
            CASE 
                WHEN ci.status = 'PAID' THEN 'PAID'
                WHEN julianday('now') - julianday(ci.due_date) <= 0 THEN 'CURRENT'
                WHEN julianday('now') - julianday(ci.due_date) <= 30 THEN '1-30 DAYS'
                WHEN julianday('now') - julianday(ci.due_date) <= 60 THEN '31-60 DAYS'
                WHEN julianday('now') - julianday(ci.due_date) <= 90 THEN '61-90 DAYS'
                ELSE 'OVER 90 DAYS'
            END as aging_bucket,
            ci.status
        FROM fact_customer_invoices ci
        JOIN fact_sales_orders so ON ci.so_id = so.so_id
        JOIN dim_customer c ON so.customer_id = c.customer_id
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} invoice records")

def load_monthly_trends(conn):
    """Load monthly trend summaries"""
    cursor = conn.cursor()
    
    print("Loading Monthly Trends...")
    
    cursor.execute("DELETE FROM analytics_monthly_trends")
    
    cursor.execute('''
        INSERT INTO analytics_monthly_trends (
            year, month, month_name, fiscal_year, fiscal_quarter,
            total_sales_orders, total_revenue, total_cost, total_profit, avg_margin_pct,
            total_customers, total_products_sold,
            total_purchase_orders, total_purchase_spend,
            inventory_value
        )
        SELECT 
            CAST(strftime('%Y', so.order_date) AS INTEGER) as year,
            CAST(strftime('%m', so.order_date) AS INTEGER) as month,
            strftime('%B', so.order_date) as month_name,
            CASE WHEN CAST(strftime('%m', so.order_date) AS INTEGER) >= 7 
                 THEN CAST(strftime('%Y', so.order_date) AS INTEGER)
                 ELSE CAST(strftime('%Y', so.order_date) AS INTEGER) - 1 END as fiscal_year,
            CAST(strftime('%m', so.order_date) AS INTEGER) / 3 + 1 as fiscal_quarter,
            COUNT(DISTINCT so.so_id) as total_sales_orders,
            SUM(so.total_amount) as total_revenue,
            SUM(COALESCE(spf.cost_of_goods_sold, so.total_amount * 0.6)) as total_cost,
            SUM(COALESCE(spf.gross_profit, so.total_amount * 0.4)) as total_profit,
            AVG(COALESCE(spf.gross_margin_pct, 40)) as avg_margin_pct,
            COUNT(DISTINCT so.customer_id) as total_customers,
            SUM(so.quantity) as total_products_sold,
            (SELECT COUNT(*) FROM fact_purchase_orders WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', so.order_date)) as total_purchase_orders,
            (SELECT COALESCE(SUM(total_cost), 0) FROM fact_purchase_orders WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', so.order_date)) as total_purchase_spend,
            (SELECT COALESCE(SUM(quantity_on_hand * average_cost), 0) FROM fact_current_inventory) as inventory_value
        FROM fact_sales_orders so
        LEFT JOIN fact_sales_profitability spf ON so.so_id = spf.so_id
        WHERE so.status != 'CANCELLED'
        GROUP BY strftime('%Y-%m', so.order_date)
        ORDER BY year, month
    ''')
    
    conn.commit()
    print(f"  Loaded {cursor.rowcount} monthly trend records")

def export_analytics_csv(conn):
    """Export analytics tables to CSV"""
    print("\nExporting analytics data to CSV...")
    
    tables = [
        'analytics_fact_sales', 'analytics_fact_purchases', 'analytics_fact_inventory',
        'analytics_customer_performance', 'analytics_product_performance',
        'analytics_supplier_performance', 'analytics_salesperson_performance',
        'analytics_invoice_aging', 'analytics_monthly_trends'
    ]
    
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        csv_path = os.path.join(OUTPUT_DIR, f"{table}.csv")
        df.to_csv(csv_path, index=False)
        print(f"  Exported {table}: {len(df)} rows")
    
    print("Analytics CSV export complete!")

def run_analytics_queries(conn):
    """Run sample analytics queries to verify data"""
    print("\n" + "=" * 60)
    print("SAMPLE ANALYTICS QUERIES")
    print("=" * 60)
    
    queries = {
        "Revenue by Month": """
            SELECT month_name || ' ' || year as period, 
                   total_revenue, total_profit, avg_margin_pct
            FROM analytics_monthly_trends
            ORDER BY year, month
        """,
        "Top 10 Products by Revenue": """
            SELECT product_name, category, units_sold, total_revenue, avg_margin_pct
            FROM analytics_product_performance
            ORDER BY total_revenue DESC
            LIMIT 10
        """,
        "Top 10 Customers by Profit": """
            SELECT customer_name, industry, region,
                   total_orders, total_revenue, total_profit
            FROM analytics_customer_performance
            ORDER BY total_profit DESC
            LIMIT 10
        """,
        "Invoice Aging Summary": """
            SELECT aging_bucket, COUNT(*) as count, SUM(amount_outstanding) as total_outstanding
            FROM analytics_invoice_aging
            WHERE status != 'PAID'
            GROUP BY aging_bucket
            ORDER BY CASE aging_bucket
                WHEN 'CURRENT' THEN 1
                WHEN '1-30 DAYS' THEN 2
                WHEN '31-60 DAYS' THEN 3
                WHEN '61-90 DAYS' THEN 4
                ELSE 5 END
        """,
        "Supplier Performance": """
            SELECT supplier_name, country, supplier_type,
                   total_orders, total_spend, on_time_rate, avg_lead_time_days
            FROM analytics_supplier_performance
            ORDER BY total_spend DESC
            LIMIT 10
        """,
        "Salesperson Leaderboard": """
            SELECT salesperson_name, region,
                   total_orders, total_revenue, avg_order_value, total_profit
            FROM analytics_salesperson_performance
            ORDER BY total_revenue DESC
        """
    }
    
    for name, query in queries.items():
        print(f"\n{name}:")
        print("-" * 50)
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

def main():
    print("=" * 60)
    print("ERP Analytics Platform - ETL Pipeline")
    print("=" * 60)
    print()
    
    conn = connect_db()
    
    # Create analytics tables
    create_analytics_tables(conn)
    
    # Load analytics data
    load_fact_sales(conn)
    load_fact_purchases(conn)
    load_fact_inventory(conn)
    load_customer_analytics(conn)
    load_product_analytics(conn)
    load_supplier_analytics(conn)
    load_salesperson_analytics(conn)
    load_invoice_aging(conn)
    load_monthly_trends(conn)
    
    # Export to CSV
    export_analytics_csv(conn)
    
    # Run sample queries
    run_analytics_queries(conn)
    
    conn.close()
    
    print()
    print("=" * 60)
    print("ETL Pipeline complete!")
    print(f"Database: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()