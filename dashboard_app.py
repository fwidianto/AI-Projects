"""
ERP Analytics Dashboard - Executive Business Intelligence
Professional dashboard for management reporting and KPI visualization.
Uses the same database connection as the main app.
"""

import sqlite3
import os
from flask import render_template, request, jsonify, Blueprint
from contextlib import contextmanager
from datetime import datetime
import json

# Dashboard Blueprint
dashboard_bp = Blueprint('dashboard', __name__, 
                         template_folder='dashboard_templates',
                         static_folder='dashboard_static')

# Database path - shared with main app
def get_db_path():
    """Get database path - uses DATABASE_PATH env var or default"""
    import os
    return os.path.expanduser(os.environ.get('DATABASE_PATH', '~/AI-Projects/database/erp_database.db'))

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

# ========================================
# EXECUTIVE DASHBOARD - KPI CARDS
# ========================================

@dashboard_bp.route('/dashboard')
def executive():
    """Executive Dashboard with high-level KPIs"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Revenue (last 12 months)
        cursor.execute("""
            SELECT COALESCE(SUM(total_revenue), 0) as revenue 
            FROM analytics_fact_sales
        """)
        revenue = cursor.fetchone()[0]
        
        # Gross Profit
        cursor.execute("""
            SELECT COALESCE(SUM(gross_profit), 0) as profit 
            FROM analytics_fact_sales
        """)
        gross_profit = cursor.fetchone()[0]
        
        # Gross Margin %
        margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
        
        # Inventory Value
        cursor.execute("SELECT COALESCE(SUM(total_value), 0) as inv_value FROM analytics_fact_inventory")
        inventory_value = cursor.fetchone()[0]
        
        # Outstanding AR
        cursor.execute("SELECT COALESCE(SUM(total_amount - amount_paid), 0) as ar FROM fact_customer_invoices WHERE status != 'PAID'")
        outstanding_ar = cursor.fetchone()[0]
        
        # Outstanding AP (fact_purchase_orders doesn't have amount_paid, use status)
        cursor.execute("SELECT COALESCE(SUM(total_cost), 0) as ap FROM fact_purchase_orders WHERE status != 'RECEIVED'")
        outstanding_ap = cursor.fetchone()[0]
        
        # Inventory Turnover (COGS / Average Inventory)
        cursor.execute("SELECT COALESCE(SUM(cost_of_goods_sold), 0) as cogs FROM analytics_fact_sales")
        cogs = cursor.fetchone()[0]
        inv_turnover = (cogs / inventory_value) if inventory_value > 0 else 0
        
        # Monthly Revenue Trend
        cursor.execute("""
            SELECT year, month, SUM(total_revenue) as revenue, SUM(total_profit) as profit
            FROM analytics_monthly_trends
            GROUP BY year, month
            ORDER BY year, month
        """)
        monthly_trend = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Top 5 Products by Revenue
        cursor.execute("""
            SELECT product_name, SUM(total_revenue) as revenue, SUM(total_profit) as profit
            FROM analytics_product_performance
            GROUP BY product_name
            ORDER BY revenue DESC
            LIMIT 5
        """)
        top_products = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Top 5 Customers by Revenue
        cursor.execute("""
            SELECT customer_name, SUM(total_revenue) as revenue, SUM(total_profit) as profit
            FROM analytics_customer_performance
            GROUP BY customer_name
            ORDER BY revenue DESC
            LIMIT 5
        """)
        top_customers = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Sales Funnel
        cursor.execute("SELECT COUNT(*) FROM fact_crm_leads")
        leads = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_quotations")
        quotations = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_orders")
        sales_orders = cursor.fetchone()[0]
        
    return render_template('dashboard/executive.html',
                         revenue=revenue,
                         gross_profit=gross_profit,
                         margin_pct=margin_pct,
                         inventory_value=inventory_value,
                         outstanding_ar=outstanding_ar,
                         outstanding_ap=outstanding_ap,
                         inv_turnover=inv_turnover,
                         monthly_trend=monthly_trend,
                         top_products=top_products,
                         top_customers=top_customers,
                         leads=leads,
                         quotations=quotations,
                         sales_orders=sales_orders)

# ========================================
# SALES ANALYTICS DASHBOARD
# ========================================

@dashboard_bp.route('/dashboard/sales')
def sales():
    """Sales Analytics Dashboard"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Revenue by Month (last 24 months)
        cursor.execute("""
            SELECT year, month, SUM(total_revenue) as revenue, SUM(total_profit) as profit
            FROM analytics_monthly_trends
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT 24
        """)
        monthly_revenue = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Revenue by Customer (top 10)
        cursor.execute("""
            SELECT customer_name, region, SUM(total_revenue) as revenue, SUM(total_profit) as profit, COUNT(*) as orders
            FROM analytics_customer_performance
            GROUP BY customer_name, region
            ORDER BY revenue DESC
            LIMIT 10
        """)
        revenue_by_customer = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Revenue by Product Category
        cursor.execute("""
            SELECT category, SUM(total_revenue) as revenue, SUM(total_profit) as profit, SUM(units_sold) as units
            FROM analytics_product_performance
            GROUP BY category
            ORDER BY revenue DESC
        """)
        revenue_by_category = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Revenue by Salesperson
        cursor.execute("""
            SELECT salesperson_name, SUM(total_revenue) as revenue, SUM(total_profit) as profit, COUNT(*) as orders
            FROM analytics_salesperson_performance
            GROUP BY salesperson_name
            ORDER BY revenue DESC
        """)
        revenue_by_salesperson = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Sales Funnel
        cursor.execute("SELECT COUNT(*) FROM fact_crm_leads")
        total_leads = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_quotations")
        total_quotes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_orders")
        total_orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_delivery_orders")
        delivered = cursor.fetchone()[0]
        
        # Conversion stats
        cursor.execute("SELECT COUNT(*) FROM fact_crm_leads WHERE lead_status = 'CONVERTED'")
        converted_leads = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_quotations WHERE status = 'ACCEPTED'")
        accepted_quotes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_orders WHERE status != 'CANCELLED'")
        completed_orders = cursor.fetchone()[0]
        
        # Top Products
        cursor.execute("""
            SELECT product_name, category, total_revenue, total_profit, units_sold
            FROM analytics_product_performance
            ORDER BY total_revenue DESC
            LIMIT 10
        """)
        top_products = [dict_from_row(row) for row in cursor.fetchall()]
        
    return render_template('dashboard/sales.html',
                         monthly_revenue=monthly_revenue,
                         revenue_by_customer=revenue_by_customer,
                         revenue_by_category=revenue_by_category,
                         revenue_by_salesperson=revenue_by_salesperson,
                         converted_leads=converted_leads,
                         total_leads=total_leads,
                         accepted_quotes=accepted_quotes,
                         total_quotes=total_quotes,
                         completed_orders=completed_orders,
                         total_orders=total_orders,
                         top_products=top_products)

# ========================================
# PURCHASING DASHBOARD
# ========================================

@dashboard_bp.route('/dashboard/purchasing')
def purchasing():
    """Purchasing Analytics Dashboard"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Purchase Spend by Month
        cursor.execute("""
            SELECT year, month, SUM(total_cost) as spend, AVG(days_to_deliver) as avg_lead_time
            FROM analytics_fact_purchases
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT 24
        """)
        monthly_spend = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Supplier Performance
        cursor.execute("""
            SELECT supplier_name, country, SUM(total_cost) as spend, COUNT(*) as orders
            FROM analytics_fact_purchases
            GROUP BY supplier_name, country
            ORDER BY spend DESC
            LIMIT 15
        """)
        supplier_performance = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Top Suppliers by Spend
        cursor.execute("""
            SELECT supplier_name, SUM(total_cost) as spend, AVG(days_to_deliver) as lead_time
            FROM analytics_fact_purchases
            GROUP BY supplier_name
            ORDER BY spend DESC
            LIMIT 10
        """)
        top_suppliers = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Purchase by Category
        cursor.execute("""
            SELECT category, SUM(total_cost) as spend, COUNT(*) as orders
            FROM analytics_fact_purchases
            GROUP BY category
            ORDER BY spend DESC
        """)
        spend_by_category = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Delivery Performance
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN on_time_delivery = 1 THEN 1 ELSE 0 END) as on_time_count,
                COUNT(*) as total_count,
                AVG(days_to_deliver) as avg_lead_time
            FROM analytics_fact_purchases
        """)
        delivery_stats = dict_from_row(cursor.fetchone())
        
    return render_template('dashboard/purchasing.html',
                         monthly_spend=monthly_spend,
                         supplier_performance=supplier_performance,
                         top_suppliers=top_suppliers,
                         spend_by_category=spend_by_category,
                         delivery_stats=delivery_stats)

# ========================================
# INVENTORY DASHBOARD
# ========================================

@dashboard_bp.route('/dashboard/inventory')
def inventory():
    """Inventory Analytics Dashboard"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Current Inventory by Warehouse
        cursor.execute("""
            SELECT warehouse_name, SUM(quantity_on_hand) as qty, SUM(total_value) as value
            FROM analytics_fact_inventory
            GROUP BY warehouse_name
            ORDER BY value DESC
        """)
        inventory_by_warehouse = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Inventory by Category
        cursor.execute("""
            SELECT category, SUM(quantity_on_hand) as qty, SUM(total_value) as value, AVG(average_cost) as avg_cost
            FROM analytics_fact_inventory
            GROUP BY category
            ORDER BY value DESC
        """)
        inventory_by_category = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Slow Moving Products - based on low turnover (high inventory, low sales)
        cursor.execute("""
            SELECT i.product_name, i.category, i.quantity_on_hand, i.average_cost, i.total_value
            FROM analytics_fact_inventory i
            JOIN analytics_product_performance p ON i.product_id = p.product_id
            ORDER BY i.quantity_on_hand DESC, p.units_sold ASC
            LIMIT 15
        """)
        slow_moving = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Fast Moving Products
        cursor.execute("""
            SELECT product_name, category, units_sold, total_revenue
            FROM analytics_product_performance
            ORDER BY units_sold DESC
            LIMIT 15
        """)
        fast_moving = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Total Inventory Value
        cursor.execute("SELECT COALESCE(SUM(total_value), 0) as total, SUM(quantity_on_hand) as qty FROM analytics_fact_inventory")
        inv_summary = dict_from_row(cursor.fetchone())
        
    return render_template('dashboard/inventory.html',
                         inventory_by_warehouse=inventory_by_warehouse,
                         inventory_by_category=inventory_by_category,
                         slow_moving=slow_moving,
                         fast_moving=fast_moving,
                         inv_summary=inv_summary)

# ========================================
# AR/AP AGING DASHBOARD
# ========================================

@dashboard_bp.route('/dashboard/aging')
def aging():
    """AR/AP Aging Analytics Dashboard"""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # AR Aging Buckets
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN days_overdue <= 0 THEN total_amount - amount_paid ELSE 0 END) as current,
                SUM(CASE WHEN days_overdue BETWEEN 1 AND 30 THEN total_amount - amount_paid ELSE 0 END) as '1-30',
                SUM(CASE WHEN days_overdue BETWEEN 31 AND 60 THEN total_amount - amount_paid ELSE 0 END) as '31-60',
                SUM(CASE WHEN days_overdue BETWEEN 61 AND 90 THEN total_amount - amount_paid ELSE 0 END) as '61-90',
                SUM(CASE WHEN days_overdue > 90 THEN total_amount - amount_paid ELSE 0 END) as '90+',
                SUM(total_amount - amount_paid) as total
            FROM analytics_invoice_aging
        """)
        ar_aging = dict_from_row(cursor.fetchone())
        
        # Overdue Invoices
        cursor.execute("""
            SELECT invoice_number, customer_name, total_amount, amount_paid, due_date, days_overdue
            FROM analytics_invoice_aging
            WHERE days_overdue > 0
            ORDER BY days_overdue DESC, total_amount DESC
            LIMIT 20
        """)
        overdue_invoices = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Top Overdue Customers
        cursor.execute("""
            SELECT customer_name, SUM(total_amount - amount_paid) as overdue_amount, COUNT(*) as overdue_count
            FROM analytics_invoice_aging
            WHERE days_overdue > 0
            GROUP BY customer_name
            ORDER BY overdue_amount DESC
            LIMIT 10
        """)
        top_overdue_customers = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Invoice Status Summary
        cursor.execute("""
            SELECT status, COUNT(*) as count, SUM(total_amount) as amount
            FROM fact_customer_invoices
            GROUP BY status
        """)
        invoice_status = [dict_from_row(row) for row in cursor.fetchall()]
        
        # AP Summary
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN status = 'PAID' THEN total_cost ELSE 0 END) as paid,
                SUM(CASE WHEN status = 'PARTIAL' THEN total_cost ELSE 0 END) as partial,
                SUM(CASE WHEN status = 'OPEN' THEN total_cost ELSE 0 END) as open,
                SUM(total_cost) as total
            FROM fact_purchase_orders
        """)
        ap_summary = dict_from_row(cursor.fetchone())
        
        # Aging Trend (last 6 months)
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', due_date) as month,
                SUM(CASE WHEN days_overdue > 90 THEN total_amount - amount_paid ELSE 0 END) as '90+',
                SUM(CASE WHEN days_overdue BETWEEN 61 AND 90 THEN total_amount - amount_paid ELSE 0 END) as '61-90',
                SUM(CASE WHEN days_overdue BETWEEN 31 AND 60 THEN total_amount - amount_paid ELSE 0 END) as '31-60',
                SUM(CASE WHEN days_overdue <= 30 THEN total_amount - amount_paid ELSE 0 END) as current
            FROM analytics_invoice_aging
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        """)
        aging_trend = [dict_from_row(row) for row in cursor.fetchall()]
        
    return render_template('dashboard/aging.html',
                         ar_aging=ar_aging,
                         overdue_invoices=overdue_invoices,
                         top_overdue_customers=top_overdue_customers,
                         invoice_status=invoice_status,
                         ap_summary=ap_summary,
                         aging_trend=aging_trend)

# ========================================
# API ENDPOINTS FOR CHARTS
# ========================================

@dashboard_bp.route('/dashboard/api/revenue-trend')
def api_revenue_trend():
    """API endpoint for revenue trend chart"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT year, month, SUM(total_revenue) as revenue, SUM(total_profit) as profit
            FROM analytics_monthly_trends
            GROUP BY year, month
            ORDER BY year, month
        """)
        data = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(data)

@dashboard_bp.route('/dashboard/api/sales-funnel')
def api_sales_funnel():
    """API endpoint for sales funnel"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fact_crm_leads")
        leads = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_quotations")
        quotes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_sales_orders")
        orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fact_delivery_orders WHERE status = 'DELIVERED'")
        delivered = cursor.fetchone()[0]
    return jsonify({
        'leads': leads,
        'quotations': quotes,
        'orders': orders,
        'delivered': delivered
    })

# ========================================
# STANDALONE DASHBOARD APP (FOR TESTING)
# ========================================

def create_dashboard_app():
    """Create standalone dashboard app"""
    app = Flask(__name__)
    app.register_blueprint(dashboard_bp)
    return app

if __name__ == '__main__':
    app = create_dashboard_app()
    app.run(debug=True, host='0.0.0.0', port=5001)