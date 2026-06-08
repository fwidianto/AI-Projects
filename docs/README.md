# ERP Analytics Platform - Technical Documentation

## Overview

This platform simulates a distribution company's ERP system with 24 months of realistic transactional data. It includes full procurement-to-pay and order-to-cash cycles, inventory tracking with FIFO costing, and analytics-ready aggregated tables.

---

## Project Structure

```
/workspace/project/
├── database/
│   └── erp_database.db          # SQLite database (all tables)
├── data/
│   └── *.csv                    # Raw data exports (17 files)
├── scripts/
│   ├── generate_erp_data.py    # Main data generator
│   └── run_etl.py               # ETL pipeline
├── output/
│   └── analytics_*.csv          # Analytics exports (9 files)
└── docs/
    ├── README.md               # This file
    ├── data_dictionary.md      # Table/field documentation
    └── erd.md                  # Entity relationship diagram
```

---

## Quick Start

### 1. Generate Data
```bash
python scripts/generate_erp_data.py
```

### 2. Run ETL Pipeline
```bash
python scripts/run_etl.py
```

### 3. Query Data
```bash
sqlite3 database/erp_database.db
```

---

## Database Schema

### Master Data Tables (Dimensions)

| Table | Description | Records |
|-------|-------------|---------|
| dim_product | Product catalog | 500 |
| dim_supplier | Supplier directory | 100 |
| dim_customer | Customer list | 1,000 |
| dim_salesperson | Sales team | 20 |
| dim_warehouse | Warehouse locations | 3 |
| dim_date | Calendar dimension | 731 |

### Transaction Tables (Facts)

| Table | Description | Records |
|-------|-------------|---------|
| fact_purchase_orders | Supplier orders | 5,500 |
| fact_goods_receipts | Inventory receipts | 6,547 |
| fact_crm_leads | Sales leads | 3,000 |
| fact_sales_quotations | Price quotes | 2,000 |
| fact_sales_orders | Customer orders | 11,000 |
| fact_delivery_orders | Shipments | 12,736 |
| fact_customer_invoices | Billing | 10,439 |
| fact_customer_payments | Payments received | 6,242 |
| fact_inventory_ledger | Inventory movements | 19,283 |
| fact_current_inventory | Current stock | 1,150 |
| fact_sales_profitability | Profit calculations | 4,419 |

### Analytics Tables

| Table | Description |
|-------|-------------|
| analytics_fact_sales | Sales with all dimensions |
| analytics_fact_purchases | Purchases with all dimensions |
| analytics_fact_inventory | Current inventory state |
| analytics_customer_performance | Customer metrics |
| analytics_product_performance | Product metrics |
| analytics_supplier_performance | Supplier metrics |
| analytics_salesperson_performance | Salesperson metrics |
| analytics_invoice_aging | AR aging buckets |
| analytics_monthly_trends | Monthly aggregates |

---

## Inventory Logic

### Movement Types

**GOODS_RECEIPT (Quantity In)**
- Triggered by: fact_goods_receipts
- Increases: Running balance
- Captures: Unit cost from PO

**DELIVERY (Quantity Out)**
- Triggered by: fact_delivery_orders
- Decreases: Running balance
- No cost captured (cost captured at receipt)

### Running Balance Calculation

```sql
running_balance = SUM(quantity_in) - SUM(quantity_out)
                 FOR EACH (product_id, warehouse_id)
                 ORDERED BY movement_date, movement_id
```

### Inventory Validation

- Sales orders can only be created for products with available inventory
- Inventory cannot go negative
- Each movement links to a source document (receipt or delivery)

---

## FIFO Costing Logic

### Cost Flow

1. **Purchase Order** → Captures unit_cost from supplier
2. **Goods Receipt** → Records unit_cost in inventory ledger
3. **Delivery Order** → No cost change (cost already in inventory)
4. **Sales Profitability** → Calculates COGS from inventory lots

### COGS Calculation

```python
# FIFO: Use oldest inventory first
def calculate_fifo_cogs(product_id, quantity_sold):
    lots = get_inventory_lots(product_id, ordered_by='movement_date')
    cogs = 0
    remaining = quantity_sold
    
    for lot in lots:
        if remaining <= 0:
            break
        qty_from_lot = min(remaining, lot.running_balance)
        cogs += qty_from_lot * lot.unit_cost
        remaining -= qty_from_lot
    
    return cogs
```

### Profitability Calculation

```
Revenue = sales_order.total_amount
COGS = calculated using FIFO from inventory
Gross Profit = Revenue - COGS
Gross Margin % = (Gross Profit / Revenue) × 100
```

---

## Data Relationships

### Procure-to-Pay Cycle

```
dim_supplier
    ↓
fact_purchase_orders (PO)
    ↓
fact_goods_receipts (GR)
    ↓
fact_inventory_ledger (increases)
    ↓
fact_current_inventory
```

### Order-to-Cash Cycle

```
dim_customer
    ↓
fact_crm_leads
    ↓
fact_sales_quotations
    ↓
fact_sales_orders (SO)
    ↓
fact_delivery_orders
    ↓
fact_inventory_ledger (decreases)
    ↓
fact_customer_invoices
    ↓
fact_customer_payments
```

### Profitability Flow

```
fact_inventory_ledger (unit_cost)
    +
fact_sales_orders (revenue)
    ↓
fact_sales_profitability
```

---

## ETL Process

### Transformation Steps

1. **Fact Sales** - Joins SO with customer, product, salesperson, profitability
2. **Fact Purchases** - Joins PO with supplier, product, calculates delivery metrics
3. **Fact Inventory** - Aggregates current inventory with product/warehouse details
4. **Customer Performance** - Aggregates by customer with AR metrics
5. **Product Performance** - Aggregates by product with sales/purchase metrics
6. **Supplier Performance** - Aggregates by supplier with on-time metrics
7. **Salesperson Performance** - Aggregates by salesperson with lead conversion
8. **Invoice Aging** - Calculates days overdue and aging buckets
9. **Monthly Trends** - Aggregates by month for trend analysis

### Aggregation Logic

- All fact tables include time dimensions (year, month, quarter, fiscal_year)
- All fact tables include relevant dimension keys for drill-down
- Analytics tables use LEFT JOINs to preserve dimensional data

---

## Sample Business Questions

### Revenue Analysis
```sql
-- Monthly revenue trend
SELECT month_name || ' ' || year as period, total_revenue
FROM analytics_monthly_trends
ORDER BY year, month;

-- Revenue by category
SELECT category, SUM(total_revenue) as revenue
FROM analytics_fact_sales
GROUP BY category
ORDER BY revenue DESC;
```

### Profitability Analysis
```sql
-- Top products by gross profit
SELECT product_name, SUM(gross_profit) as total_profit
FROM analytics_fact_sales
GROUP BY product_id
ORDER BY total_profit DESC
LIMIT 10;

-- Customer profitability
SELECT customer_name, total_revenue, total_profit, avg_margin_pct
FROM analytics_customer_performance
ORDER BY total_profit DESC;
```

### Inventory Analysis
```sql
-- Inventory value by warehouse
SELECT warehouse_name, SUM(total_value) as inventory_value
FROM analytics_fact_inventory
GROUP BY warehouse_id;

-- Low stock products
SELECT product_name, quantity_on_hand, total_value
FROM analytics_fact_inventory
WHERE quantity_on_hand < 50
ORDER BY quantity_on_hand;
```

### AR Aging Analysis
```sql
-- Overdue invoices by aging bucket
SELECT aging_bucket, COUNT(*) as count, SUM(amount_outstanding) as total
FROM analytics_invoice_aging
WHERE status != 'PAID'
GROUP BY aging_bucket;

-- Top overdue customers
SELECT customer_name, SUM(amount_outstanding) as outstanding
FROM analytics_invoice_aging
WHERE days_overdue > 0
GROUP BY customer_id
ORDER BY outstanding DESC;
```

### Supplier Performance
```sql
-- Best suppliers by on-time rate
SELECT supplier_name, total_orders, on_time_rate, avg_lead_time_days
FROM analytics_supplier_performance
ORDER BY on_time_rate DESC;

-- Highest spend suppliers
SELECT supplier_name, total_spend, product_variety
FROM analytics_supplier_performance
ORDER BY total_spend DESC;
```

---

## Data Quality Notes

### Realistic Data Characteristics

1. **Partial Receipts**: POs may have multiple receipts
2. **Late Deliveries**: ~15% of deliveries are delayed
3. **Quote Conversion**: ~40% of leads become quotations
4. **Order Conversion**: ~40% of quotations become orders
5. **Cancellation Rate**: ~5% of sales orders are cancelled
6. **Late Payments**: ~30% of customers pay late
7. **Unpaid Invoices**: Some invoices remain outstanding

### Referential Integrity

- All foreign keys are properly linked
- Inventory movements reference source documents
- Profitability calculations link to actual inventory costs

---

## Time Period Coverage

- **Start Date**: July 1, 2023
- **End Date**: June 30, 2025
- **Duration**: 24 months (2 years)
- **Fiscal Year**: July - June

---

## Technology Stack

- **Database**: SQLite 3
- **Language**: Python 3
- **Libraries**: 
  - faker (data generation)
  - pandas (data manipulation)
  - sqlite3 (database connectivity)

---

## File Outputs

### Database
- `database/erp_database.db` - Complete SQLite database

### CSV Exports
- `data/` - 17 raw table exports
- `output/` - 9 analytics table exports

### Documentation
- `docs/data_dictionary.md` - Detailed table specifications
- `docs/erd.md` - Entity relationship diagrams

---

## Success Criteria Verification

| Question | Table/Query |
|----------|-------------|
| What is revenue by month? | analytics_monthly_trends |
| What is gross profit by product? | analytics_product_performance |
| Which customers are most profitable? | analytics_customer_performance |
| Which suppliers provide best margins? | analytics_supplier_performance |
| What inventory is aging? | analytics_fact_inventory (last_receipt_date) |
| Which invoices are overdue? | analytics_invoice_aging |

---

*ERP Analytics Platform v1.0*
*Generated for demonstration and development purposes*