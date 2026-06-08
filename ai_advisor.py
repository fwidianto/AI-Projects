"""
AI Executive Advisor - Decision Support System
Generates business insights, detects risks, identifies opportunities,
provides recommendations, and forecasts future performance.
"""

import sqlite3
import os
from flask import render_template, Blueprint, current_app
from contextlib import contextmanager
from datetime import datetime, timedelta
import json

# Blueprint
ai_advisor_bp = Blueprint('ai_advisor', __name__, 
                          template_folder='ai_templates')

def get_db_path():
    return os.path.expanduser(os.environ.get('DATABASE_PATH', '~/AI-Projects/database/erp_database.db'))

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row):
    return dict(zip(row.keys(), row))

# ========================================
# ANALYSIS HELPERS
# ========================================

def get_metric_change(current, previous):
    """Calculate percentage change between two values"""
    if previous and previous != 0:
        return ((current - previous) / previous) * 100
    return 0

def get_trend_direction(pct_change):
    """Return trend direction based on percentage change"""
    if pct_change > 2:
        return 'up'
    elif pct_change < -2:
        return 'down'
    return 'stable'

def get_risk_level(score):
    """Convert risk score to level"""
    if score >= 75:
        return 'Critical'
    elif score >= 50:
        return 'High'
    elif score >= 25:
        return 'Medium'
    return 'Low'

def format_currency(value):
    return f"${value:,.0f}"

def format_pct(value):
    return f"{value:.1f}%"

# ========================================
# EXECUTIVE SUMMARY DATA
# ========================================

def get_executive_summary():
    """Generate comprehensive executive summary"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Revenue Summary
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_revenue), 0) as revenue,
                COALESCE(SUM(gross_profit), 0) as profit,
                COUNT(*) as order_count
            FROM analytics_fact_sales
        """)
        sales_data = dict_from_row(cursor.fetchone())
        
        # Current month
        cursor.execute("""
            SELECT COALESCE(SUM(total_revenue), 0) as revenue
            FROM analytics_fact_sales
            WHERE year = (SELECT MAX(year) FROM analytics_fact_sales)
              AND month = (SELECT MAX(month) FROM analytics_fact_sales WHERE year = (SELECT MAX(year) FROM analytics_fact_sales))
        """)
        current_month_revenue = cursor.fetchone()[0]
        
        # Previous month
        cursor.execute("""
            SELECT COALESCE(SUM(total_revenue), 0) as revenue
            FROM analytics_fact_sales
            WHERE (year * 12 + month) = 
                  (SELECT MAX(year * 12 + month) - 1 FROM analytics_fact_sales)
        """)
        prev_month_revenue = cursor.fetchone()[0]
        
        revenue_change = get_metric_change(current_month_revenue, prev_month_revenue)
        
        # Profitability Summary
        margin_pct = (sales_data['profit'] / sales_data['revenue'] * 100) if sales_data['revenue'] > 0 else 0
        
        cursor.execute("""
            SELECT COALESCE(AVG(avg_margin_pct), 0) as avg_margin
            FROM analytics_monthly_trends
        """)
        avg_margin = cursor.fetchone()[0]
        
        # Inventory Summary
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_value), 0) as inv_value,
                COUNT(*) as product_count
            FROM analytics_fact_inventory
        """)
        inv_data = dict_from_row(cursor.fetchone())
        
        # Slow moving inventory
        cursor.execute("""
            SELECT COUNT(*) as slow_count
            FROM analytics_fact_inventory i
            JOIN analytics_product_performance p ON i.product_id = p.product_id
            WHERE i.quantity_on_hand > p.units_sold * 2
        """)
        slow_inv = cursor.fetchone()[0]
        slow_inv_pct = (slow_inv / inv_data['product_count'] * 100) if inv_data['product_count'] > 0 else 0
        
        # AR Summary
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_amount - amount_paid), 0) as outstanding_ar,
                COUNT(*) as total_invoices
            FROM fact_customer_invoices
            WHERE status != 'PAID'
        """)
        ar_data = dict_from_row(cursor.fetchone())
        
        # Overdue AR
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount - amount_paid), 0) as overdue
            FROM analytics_invoice_aging
            WHERE days_overdue > 0
        """)
        overdue_ar = cursor.fetchone()[0]
        overdue_pct = (overdue_ar / ar_data['outstanding_ar'] * 100) if ar_data['outstanding_ar'] > 0 else 0
        
        # Supplier Summary
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT supplier_id) as supplier_count,
                COALESCE(SUM(total_cost), 0) as total_spend
            FROM analytics_fact_purchases
        """)
        supplier_data = dict_from_row(cursor.fetchone())
        
        # On-time delivery rate
        cursor.execute("""
            SELECT 
                CAST(SUM(CASE WHEN on_time_delivery = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as on_time_rate
            FROM analytics_fact_purchases
        """)
        on_time_rate = cursor.fetchone()[0] or 0
        
    return {
        'revenue': {
            'current': sales_data['revenue'],
            'formatted': format_currency(sales_data['revenue']),
            'monthly_current': current_month_revenue,
            'monthly_prev': prev_month_revenue,
            'monthly_change': revenue_change,
            'trend': get_trend_direction(revenue_change),
            'order_count': sales_data['order_count']
        },
        'profitability': {
            'profit': sales_data['profit'],
            'formatted': format_currency(sales_data['profit']),
            'margin_pct': margin_pct,
            'avg_margin': avg_margin,
            'trend': get_trend_direction(margin_pct - avg_margin)
        },
        'inventory': {
            'value': inv_data['inv_value'],
            'formatted': format_currency(inv_data['inv_value']),
            'product_count': inv_data['product_count'],
            'slow_moving_count': slow_inv,
            'slow_moving_pct': slow_inv_pct,
            'risk_level': get_risk_level(slow_inv_pct * 2)
        },
        'accounts_receivable': {
            'outstanding': ar_data['outstanding_ar'],
            'formatted': format_currency(ar_data['outstanding_ar']),
            'overdue': overdue_ar,
            'overdue_pct': overdue_pct,
            'risk_level': get_risk_level(overdue_pct * 2)
        },
        'supplier': {
            'count': supplier_data['supplier_count'],
            'total_spend': supplier_data['total_spend'],
            'formatted': format_currency(supplier_data['total_spend']),
            'on_time_rate': on_time_rate
        }
    }

# ========================================
# INSIGHT ENGINE
# ========================================

def get_insights():
    """Generate data-driven insights across business areas"""
    insights = {
        'sales': [],
        'inventory': [],
        'ar': [],
        'supplier': [],
        'customer': []
    }
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Sales Insights
        cursor.execute("""
            SELECT 
                year, month,
                SUM(total_revenue) as revenue,
                SUM(total_profit) as profit,
                AVG(avg_margin_pct) as margin
            FROM analytics_monthly_trends
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT 6
        """)
        monthly_data = [dict_from_row(row) for row in cursor.fetchall()]
        
        if len(monthly_data) >= 2:
            current = monthly_data[0]
            previous = monthly_data[1]
            
            rev_change = get_metric_change(current['revenue'], previous['revenue'])
            if abs(rev_change) > 5:
                insights['sales'].append({
                    'type': 'revenue_trend',
                    'text': f"Revenue {get_trend_direction(rev_change).replace('up', 'increased').replace('down', 'decreased')} {abs(rev_change):.1f}% month-over-month",
                    'metric': f"{rev_change:+.1f}%",
                    'current': current['revenue'],
                    'previous': previous['revenue']
                })
            
            margin_change = current['margin'] - previous['margin']
            if abs(margin_change) > 2:
                insights['sales'].append({
                    'type': 'margin_trend',
                    'text': f"Gross margin {get_trend_direction(margin_change).replace('up', 'improved').replace('down', 'declined')} {abs(margin_change):.1f} percentage points",
                    'metric': f"{margin_change:+.1f}pp",
                    'current': current['margin'],
                    'previous': previous['margin']
                })
        
        # Top performing category
        cursor.execute("""
            SELECT category, SUM(total_revenue) as revenue, AVG(gross_margin_pct) as margin
            FROM analytics_fact_sales
            GROUP BY category
            ORDER BY revenue DESC
            LIMIT 1
        """)
        top_cat = dict_from_row(cursor.fetchone())
        if top_cat:
            insights['sales'].append({
                'type': 'top_category',
                'text': f"Top revenue category: {top_cat['category']}",
                'metric': format_currency(top_cat['revenue']),
                'margin': top_cat['margin']
            })
        
        # Inventory Insights
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN i.quantity_on_hand > p.units_sold * 3 THEN 1 ELSE 0 END) as slow_moving
            FROM analytics_fact_inventory i
            JOIN analytics_product_performance p ON i.product_id = p.product_id
        """)
        inv_analysis = dict_from_row(cursor.fetchone())
        slow_pct = (inv_analysis['slow_moving'] / inv_analysis['total'] * 100) if inv_analysis['total'] > 0 else 0
        
        if slow_pct > 15:
            insights['inventory'].append({
                'type': 'slow_moving',
                'text': f"Slow-moving inventory increased to {slow_pct:.1f}% of products",
                'metric': f"{slow_pct:.1f}%",
                'count': inv_analysis['slow_moving']
            })
        
        # High-value inventory sitting
        cursor.execute("""
            SELECT SUM(total_value) as high_value
            FROM analytics_fact_inventory
            WHERE quantity_on_hand > 500
        """)
        high_value = cursor.fetchone()[0] or 0
        if high_value > 100000:
            insights['inventory'].append({
                'type': 'overstock',
                'text': "Significant inventory overstock detected",
                'metric': format_currency(high_value),
                'category': 'high_value_overstock'
            })
        
        # AR Insights
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN days_overdue > 90 THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN days_overdue BETWEEN 31 AND 90 THEN 1 ELSE 0 END) as moderate
            FROM analytics_invoice_aging
            WHERE days_overdue > 0
        """)
        ar_analysis = dict_from_row(cursor.fetchone())
        overdue_count = ar_analysis['critical'] + ar_analysis['moderate']
        
        if overdue_count > 0:
            insights['ar'].append({
                'type': 'overdue_invoices',
                'text': f"{overdue_count} invoices are overdue",
                'critical': ar_analysis['critical'],
                'moderate': ar_analysis['moderate']
            })
        
        # Customer concentration
        cursor.execute("""
            SELECT 
                customer_name,
                SUM(total_revenue) as revenue,
                (CAST(SUM(total_revenue) AS FLOAT) / (SELECT SUM(total_revenue) FROM analytics_customer_performance) * 100) as pct
            FROM analytics_customer_performance
            GROUP BY customer_name
            ORDER BY revenue DESC
            LIMIT 1
        """)
        top_customer = dict_from_row(cursor.fetchone())
        if top_customer and top_customer['pct'] > 25:
            insights['customer'].append({
                'type': 'concentration',
                'text': f"Customer concentration risk: {top_customer['customer_name']} represents {top_customer['pct']:.1f}% of revenue",
                'metric': f"{top_customer['pct']:.1f}%",
                'risk': 'high' if top_customer['pct'] > 40 else 'medium'
            })
        
        # Supplier insights
        cursor.execute("""
            SELECT 
                supplier_name,
                SUM(total_cost) as spend,
                AVG(days_to_deliver) as avg_lead_time
            FROM analytics_fact_purchases
            GROUP BY supplier_name
            ORDER BY spend DESC
            LIMIT 1
        """)
        top_supplier = dict_from_row(cursor.fetchone())
        if top_supplier:
            insights['supplier'].append({
                'type': 'top_supplier',
                'text': f"Top supplier: {top_supplier['supplier_name']} with ${top_supplier['spend']:,.0f} spend",
                'metric': format_currency(top_supplier['spend']),
                'lead_time': f"{top_supplier['avg_lead_time']:.0f} days"
            })
        
    return insights

# ========================================
# RISK DETECTION ENGINE
# ========================================

def get_risks():
    """Detect and score business risks"""
    risks = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Customer Concentration Risk
        cursor.execute("""
            SELECT 
                customer_name,
                SUM(total_revenue) as revenue,
                (CAST(SUM(total_revenue) AS FLOAT) / (SELECT SUM(total_revenue) FROM analytics_customer_performance) * 100) as pct
            FROM analytics_customer_performance
            GROUP BY customer_name
            ORDER BY revenue DESC
            LIMIT 1
        """)
        top_customer = dict_from_row(cursor.fetchone())
        if top_customer:
            score = min(100, top_customer['pct'] * 2)
            if score >= 50:
                risks.append({
                    'category': 'Customer',
                    'name': 'High Customer Concentration',
                    'level': get_risk_level(score),
                    'score': score,
                    'reasoning': f"{top_customer['customer_name']} accounts for {top_customer['pct']:.1f}% of total revenue",
                    'impact': 'Business disruption if this customer reduces orders',
                    'indicator': f"{top_customer['pct']:.1f}% revenue concentration"
                })
        
        # Slow-Moving Inventory Risk
        cursor.execute("""
            SELECT COUNT(*) as slow_count
            FROM analytics_fact_inventory i
            JOIN analytics_product_performance p ON i.product_id = p.product_id
            WHERE i.quantity_on_hand > p.units_sold * 3
        """)
        slow_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM analytics_fact_inventory")
        total_inv = cursor.fetchone()[0]
        slow_pct = (slow_count / total_inv * 100) if total_inv > 0 else 0
        
        score = min(100, slow_pct * 3)
        if slow_pct > 10:
            risks.append({
                'category': 'Inventory',
                'name': 'Slow-Moving Inventory',
                'level': get_risk_level(score),
                'score': score,
                'reasoning': f"{slow_count} products ({slow_pct:.1f}%) have inventory 3x their sales rate",
                'impact': 'Tied-up capital and potential obsolescence',
                'indicator': f"{slow_pct:.1f}% slow-moving products"
            })
        
        # Overdue AR Risk
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN days_overdue > 90 THEN total_amount - amount_paid ELSE 0 END) as critical,
                SUM(CASE WHEN days_overdue > 0 THEN total_amount - amount_paid ELSE 0 END) as total_overdue,
                COUNT(*) as overdue_count
            FROM analytics_invoice_aging
            WHERE days_overdue > 0
        """)
        ar_risk = dict_from_row(cursor.fetchone())
        
        if ar_risk['total_overdue'] > 0:
            critical_pct = (ar_risk['critical'] / ar_risk['total_overdue'] * 100) if ar_risk['total_overdue'] > 0 else 0
            score = min(100, critical_pct * 2)
            risks.append({
                'category': 'Financial',
                'name': 'Overdue Receivables',
                'level': get_risk_level(score),
                'score': score,
                'reasoning': f"${ar_risk['total_overdue']:,.0f} overdue, ${ar_risk['critical']:,.0f} is 90+ days past due",
                'impact': 'Cash flow impact and potential bad debt',
                'indicator': f"{ar_risk['overdue_count']} overdue invoices"
            })
        
        # Supplier Dependency Risk
        cursor.execute("""
            SELECT 
                supplier_name,
                SUM(total_cost) as spend,
                (CAST(SUM(total_cost) AS FLOAT) / (SELECT SUM(total_cost) FROM analytics_fact_purchases) * 100) as pct
            FROM analytics_fact_purchases
            GROUP BY supplier_name
            ORDER BY spend DESC
            LIMIT 1
        """)
        top_supplier = dict_from_row(cursor.fetchone())
        if top_supplier and top_supplier['pct'] > 35:
            score = min(100, top_supplier['pct'] * 2)
            risks.append({
                'category': 'Supplier',
                'name': 'Supplier Dependency',
                'level': get_risk_level(score),
                'score': score,
                'reasoning': f"{top_supplier['supplier_name']} accounts for {top_supplier['pct']:.1f}% of purchases",
                'impact': 'Supply chain disruption risk if supplier has issues',
                'indicator': f"{top_supplier['pct']:.1f}% purchase concentration"
            })
        
        # Margin Compression Risk
        cursor.execute("""
            SELECT AVG(avg_margin_pct) as avg_margin
            FROM analytics_monthly_trends
            ORDER BY year DESC, month DESC
            LIMIT 3
        """)
        recent_margins = [row[0] for row in cursor.fetchall()]
        if len(recent_margins) >= 3 and recent_margins[0] < recent_margins[2]:
            decline = recent_margins[2] - recent_margins[0]
            if decline > 3:
                risks.append({
                    'category': 'Financial',
                    'name': 'Margin Compression',
                    'level': get_risk_level(decline * 10),
                    'score': min(100, decline * 10),
                    'reasoning': f"Gross margin declined {decline:.1f} percentage points over 3 months",
                    'impact': 'Reduced profitability',
                    'indicator': f"From {recent_margins[2]:.1f}% to {recent_margins[0]:.1f}%"
                })
        
    # Sort by score descending
    risks.sort(key=lambda x: x['score'], reverse=True)
    return risks

# ========================================
# OPPORTUNITY ENGINE
# ========================================

def get_opportunities():
    """Identify business opportunities"""
    opportunities = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # High-Growth Customers
        cursor.execute("""
            SELECT 
                customer_name,
                SUM(total_revenue) as revenue,
                COUNT(*) as order_count
            FROM analytics_customer_performance
            GROUP BY customer_name
            HAVING revenue > (SELECT AVG(total_revenue) FROM analytics_customer_performance) * 1.5
            ORDER BY revenue DESC
            LIMIT 3
        """)
        for row in cursor.fetchall():
            opp = dict_from_row(row)
            opportunities.append({
                'type': 'High-Growth Customer',
                'title': f"Expand relationship with {opp['customer_name']}",
                'impact': format_currency(opp['revenue']),
                'reasoning': f"Customer generates {opp['order_count']} orders above average"
            })
        
        # Fast-Moving Products
        cursor.execute("""
            SELECT 
                product_name,
                category,
                units_sold,
                total_revenue,
                avg_margin_pct
            FROM analytics_product_performance
            WHERE units_sold > (SELECT AVG(units_sold) FROM analytics_product_performance)
            ORDER BY units_sold DESC
            LIMIT 3
        """)
        for row in cursor.fetchall():
            opp = dict_from_row(row)
            opportunities.append({
                'type': 'Fast-Moving Product',
                'title': f"Increase stock of {opp['product_name']}",
                'impact': f"{opp['units_sold']:,} units sold",
                'reasoning': f"Strong demand in {opp['category']} with {opp['avg_margin_pct']:.1f}% margin"
            })
        
        # High-Margin Products
        cursor.execute("""
            SELECT 
                product_name,
                avg_margin_pct,
                units_sold
            FROM analytics_product_performance
            WHERE avg_margin_pct > (SELECT AVG(avg_margin_pct) FROM analytics_product_performance) * 1.2
            AND units_sold > 10
            ORDER BY avg_margin_pct DESC
            LIMIT 3
        """)
        for row in cursor.fetchall():
            opp = dict_from_row(row)
            opportunities.append({
                'type': 'High-Margin Product',
                'title': f"Promote {opp['product_name']}",
                'impact': f"{opp['avg_margin_pct']:.1f}% margin",
                'reasoning': f"Above-average margin with {opp['units_sold']} units sold"
            })
        
        # Efficient Suppliers
        cursor.execute("""
            SELECT 
                supplier_name,
                AVG(days_to_deliver) as avg_lead,
                SUM(total_cost) as spend
            FROM analytics_fact_purchases
            GROUP BY supplier_name
            HAVING avg_lead < (SELECT AVG(days_to_deliver) FROM analytics_fact_purchases)
            ORDER BY spend DESC
            LIMIT 3
        """)
        for row in cursor.fetchall():
            opp = dict_from_row(row)
            opportunities.append({
                'type': 'Supplier Efficiency',
                'title': f"Increase orders with {opp['supplier_name']}",
                'impact': f"{opp['avg_lead']:.0f} day lead time",
                'reasoning': f"Below-average lead time, ${opp['spend']:,.0f} annual spend"
            })
        
    return opportunities

# ========================================
# RECOMMENDATION ENGINE
# ========================================

def get_recommendations():
    """Generate actionable recommendations based on data"""
    recommendations = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check slow inventory
        cursor.execute("""
            SELECT COUNT(*) as slow_count
            FROM analytics_fact_inventory i
            JOIN analytics_product_performance p ON i.product_id = p.product_id
            WHERE i.quantity_on_hand > p.units_sold * 3
        """)
        slow_count = cursor.fetchone()[0]
        if slow_count > 5:
            recommendations.append({
                'category': 'Inventory',
                'observation': f"{slow_count} products have excess inventory (stock 3x sales rate)",
                'actions': [
                    "Launch promotional discounts for slow-moving items",
                    "Bundle slow-moving products with fast sellers",
                    "Reduce future purchase quantities for these products",
                    "Consider liquidating oldest stock"
                ],
                'benefits': "Reduce carrying costs and free up capital",
                'priority': 'High'
            })
        
        # Check AR aging
        cursor.execute("""
            SELECT COUNT(*) as overdue_count,
                   SUM(CASE WHEN days_overdue > 60 THEN 1 ELSE 0 END) as critical
            FROM analytics_invoice_aging
            WHERE days_overdue > 0
        """)
        ar_stats = dict_from_row(cursor.fetchone())
        if ar_stats['critical'] > 0:
            recommendations.append({
                'category': 'Collections',
                'observation': f"{ar_stats['overdue_count']} overdue invoices, {ar_stats['critical']} are 60+ days past due",
                'actions': [
                    "Contact customers with 60+ day overdue invoices",
                    "Escalate critical accounts for legal action if appropriate",
                    "Review credit terms for repeat late payers",
                    "Consider early payment discounts for future invoices"
                ],
                'benefits': "Improve cash flow and reduce bad debt risk",
                'priority': 'Critical' if ar_stats['critical'] > 3 else 'High'
            })
        
        # Check margin trends
        cursor.execute("""
            SELECT AVG(avg_margin_pct) as recent_avg
            FROM analytics_monthly_trends
            WHERE (year * 12 + month) >= (SELECT MAX(year * 12 + month) FROM analytics_monthly_trends) - 3
        """)
        recent_margin = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(avg_margin_pct) FROM analytics_monthly_trends")
        overall_margin = cursor.fetchone()[0] or 0
        
        if recent_margin < overall_margin * 0.95:
            recommendations.append({
                'category': 'Pricing',
                'observation': f"Gross margin trending down: {recent_margin:.1f}% vs {overall_margin:.1f}% average",
                'actions': [
                    "Review pricing strategy for low-margin products",
                    "Negotiate better terms with suppliers",
                    "Identify products with best margin for focused selling",
                    "Analyze cost structure for savings opportunities"
                ],
                'benefits': "Protect and improve profitability",
                'priority': 'Medium'
            })
        
        # Check customer concentration
        cursor.execute("""
            SELECT 
                CAST(SUM(tc.total_revenue) AS FLOAT) / 
                (SELECT SUM(total_revenue) FROM analytics_customer_performance) * 100 as concentration
            FROM analytics_customer_performance tc
            GROUP BY customer_name
            ORDER BY concentration DESC
            LIMIT 1
        """)
        max_conc = cursor.fetchone()[0] or 0
        if max_conc > 30:
            recommendations.append({
                'category': 'Customer Development',
                'observation': f"Top customer represents {max_conc:.1f}% of revenue (concentration risk)",
                'actions': [
                    "Develop upselling strategy for existing customers",
                    "Increase marketing to acquire new customers",
                    "Create loyalty programs to retain customers",
                    "Diversify customer base across industries"
                ],
                'benefits': "Reduce dependency risk and grow revenue",
                'priority': 'Medium'
            })
        
    return recommendations

# ========================================
# FORECASTING ENGINE
# ========================================

def get_forecasts():
    """Generate forecasts using moving averages and trends"""
    forecasts = {
        'revenue': {},
        'profit': {},
        'inventory': {},
        'ar': {}
    }
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Revenue Forecast
        cursor.execute("""
            SELECT 
                year, month, month_name,
                SUM(total_revenue) as total_revenue,
                SUM(total_profit) as total_profit
            FROM analytics_monthly_trends
            GROUP BY year, month
            ORDER BY year, month
        """)
        monthly_data = [dict_from_row(row) for row in cursor.fetchall()]
        
        if len(monthly_data) >= 3:
            revenues = [d['total_revenue'] for d in monthly_data]
            profits = [d['total_profit'] for d in monthly_data]
            
            # Simple moving average
            avg_revenue = sum(revenues[-3:]) / 3
            avg_profit = sum(profits[-3:]) / 3
            
            # Trend calculation
            if len(revenues) >= 6:
                first_half = sum(revenues[:3]) / 3
                second_half = sum(revenues[-3:]) / 3
                trend_factor = second_half / first_half if first_half > 0 else 1
            else:
                trend_factor = 1
            
            # Generate forecasts
            for days, label in [(30, '30d'), (90, '90d'), (180, '180d')]:
                months = days / 30
                confidence = 0.9 if len(monthly_data) >= 12 else 0.7
                
                forecasted_revenue = avg_revenue * months * trend_factor
                forecasted_profit = avg_profit * months * trend_factor
                
                forecasts['revenue'][label] = {
                    'value': forecasted_revenue,
                    'formatted': format_currency(forecasted_revenue),
                    'trend': 'up' if trend_factor > 1 else 'down',
                    'confidence': confidence * 100
                }
                
                forecasts['profit'][label] = {
                    'value': forecasted_profit,
                    'formatted': format_currency(forecasted_profit),
                    'trend': 'up' if trend_factor > 1 else 'down',
                    'confidence': confidence * 100
                }
        
        # Inventory Forecast
        cursor.execute("SELECT SUM(total_value) as inv_value FROM analytics_fact_inventory")
        current_inv = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT AVG(quantity_on_hand) as avg_stock
            FROM analytics_fact_inventory
        """)
        avg_stock = cursor.fetchone()[0] or 0
        
        for days, label in [(30, '30d'), (90, '90d'), (180, '180d')]:
            months = days / 30
            forecasted_inv = avg_stock * months
            forecasts['inventory'][label] = {
                'value': forecasted_inv,
                'formatted': format_currency(forecasted_inv),
                'trend': 'stable',
                'confidence': 75
            }
        
        # AR Forecast
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount - amount_paid), 0) as ar
            FROM fact_customer_invoices
            WHERE status != 'PAID'
        """)
        current_ar = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT AVG(total_amount - amount_paid) as avg_ar
            FROM fact_customer_invoices
            WHERE status != 'PAID'
        """)
        avg_ar = cursor.fetchone()[0] or 0
        
        for days, label in [(30, '30d'), (90, '90d'), (180, '180d')]:
            months = days / 30
            forecasted_ar = avg_ar * months if avg_ar > 0 else current_ar
            forecasts['ar'][label] = {
                'value': forecasted_ar,
                'formatted': format_currency(forecasted_ar),
                'trend': 'stable',
                'confidence': 70
            }
        
        # Historical data for charts
        forecasts['historical'] = monthly_data[-12:] if len(monthly_data) > 12 else monthly_data
        
    return forecasts

# ========================================
# EXECUTIVE MORNING BRIEF
# ========================================

def get_executive_brief():
    """Generate daily executive brief"""
    summary = get_executive_summary()
    insights = get_insights()
    risks = get_risks()
    recommendations = get_recommendations()
    
    # Get top insight
    top_insight = "All metrics within normal ranges"
    if insights['sales']:
        top_insight = insights['sales'][0]['text']
    elif insights['inventory']:
        top_insight = insights['inventory'][0]['text']
    
    # Get top risk
    top_risk = "No critical risks identified"
    if risks:
        top_risk = f"{risks[0]['name']}: {risks[0]['level']} risk"
    
    # Get top recommendation
    top_recommendation = "Continue monitoring key metrics"
    if recommendations:
        top_recommendation = recommendations[0]['observation'][:100] + "..."
    
    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'date_formatted': datetime.now().strftime('%B %d, %Y'),
        'revenue': summary['revenue'],
        'profitability': summary['profitability'],
        'inventory_risk': summary['inventory']['risk_level'],
        'ar_risk': summary['accounts_receivable']['risk_level'],
        'top_insight': top_insight,
        'top_risk': top_risk,
        'top_recommendation': top_recommendation,
        'key_metrics': {
            'revenue_change': summary['revenue']['monthly_change'],
            'margin': summary['profitability']['margin_pct'],
            'slow_inventory_pct': summary['inventory']['slow_moving_pct'],
            'overdue_pct': summary['accounts_receivable']['overdue_pct']
        },
        'risk_count': len([r for r in risks if r['level'] in ['High', 'Critical']]),
        'opportunity_count': len(get_opportunities()),
        'recommendation_count': len(recommendations)
    }

# ========================================
# ROUTES
# ========================================

@ai_advisor_bp.route('/ai-advisor')
def index():
    """AI Executive Advisor - Main Dashboard"""
    summary = get_executive_summary()
    insights = get_insights()
    risks = get_risks()
    opportunities = get_opportunities()
    recommendations = get_recommendations()
    forecasts = get_forecasts()
    brief = get_executive_brief()
    
    return render_template('ai_advisor/index.html',
                         summary=summary,
                         insights=insights,
                         risks=risks,
                         opportunities=opportunities,
                         recommendations=recommendations,
                         forecasts=forecasts,
                         brief=brief)

@ai_advisor_bp.route('/ai-advisor/brief')
def morning_brief():
    """Daily Executive Brief"""
    brief = get_executive_brief()
    return render_template('ai_advisor/brief.html', brief=brief)

@ai_advisor_bp.route('/ai-advisor/risks')
def risk_report():
    """Detailed Risk Report"""
    risks = get_risks()
    return render_template('ai_advisor/risks.html', risks=risks)

@ai_advisor_bp.route('/ai-advisor/opportunities')
def opportunity_report():
    """Detailed Opportunity Report"""
    opportunities = get_opportunities()
    return render_template('ai_advisor/opportunities.html', opportunities=opportunities)

# Export blueprint for registration
__all__ = ['ai_advisor_bp']