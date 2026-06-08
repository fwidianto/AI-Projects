# ERP Analytics Platform - Data Dictionary

## Overview

This document describes all tables in the ERP Analytics database, their fields, data types, and relationships.

---

## Dimension Tables (Master Data)

### dim_product
Products sold by the company.

| Field | Type | Description |
|-------|------|-------------|
| product_id | TEXT (PK) | Unique product identifier (format: PRD-XXXXXXXX) |
| sku | TEXT | Stock Keeping Unit - unique product code |
| product_name | TEXT | Product description name |
| category | TEXT | Product category (16 categories) |
| default_selling_price | REAL | Standard selling price |
| unit_cost | REAL | Last known unit cost (from purchase) |
| is_active | INTEGER | 1=Active, 0=Inactive |

**Sample Values:**
- PRD-00000001, SKU-00001, "USB-C Cable", Electronics, 12.99

---

### dim_supplier
Vendor companies that supply products.

| Field | Type | Description |
|-------|------|-------------|
| supplier_id | TEXT (PK) | Unique supplier identifier (format: SUP-XXXXXXXX) |
| supplier_name | TEXT | Supplier company name |
| country | TEXT | Country of origin |
| supplier_type | TEXT | Manufacturer, Distributor, Importer, Wholesaler |
| contact_name | TEXT | Primary contact person |
| email | TEXT | Contact email |
| phone | TEXT | Contact phone |
| is_active | INTEGER | 1=Active, 0=Inactive |

---

### dim_customer
Companies that purchase products from the company.

| Field | Type | Description |
|-------|------|-------------|
| customer_id | TEXT (PK) | Unique customer identifier (format: CUST-XXXXXXXX) |
| customer_name | TEXT | Customer company name |
| industry | TEXT | Business industry (15 industries) |
| region | TEXT | Geographic region (North, South, East, West, Central) |
| country | TEXT | Country location |
| credit_limit | REAL | Maximum credit allowed |
| payment_terms_days | INTEGER | Payment due days (15, 30, 45, 60) |
| is_active | INTEGER | 1=Active, 0=Inactive |

---

### dim_salesperson
Sales representatives who manage customer relationships.

| Field | Type | Description |
|-------|------|-------------|
| salesperson_id | TEXT (PK) | Unique identifier (format: SP-XXXXXXXX) |
| first_name | TEXT | First name |
| last_name | TEXT | Last name |
| email | TEXT | Work email |
| phone | TEXT | Work phone |
| region | TEXT | Assigned sales region |
| hire_date | DATE | Date hired |

---

### dim_warehouse
Physical locations where inventory is stored.

| Field | Type | Description |
|-------|------|-------------|
| warehouse_id | TEXT (PK) | Unique identifier (WH-001, WH-002, WH-003) |
| warehouse_name | TEXT | Descriptive name |
| location | TEXT | City, State location |
| capacity | INTEGER | Storage capacity units |
| manager_name | TEXT | Warehouse manager |

**Warehouses:**
- WH-001: Main Distribution Center, Chicago, IL
- WH-002: East Coast Hub, Newark, NJ
- WH-003: West Coast Center, Los Angeles, CA

---

### dim_date
Calendar dimension for time-based analysis.

| Field | Type | Description |
|-------|------|-------------|
| date_id | TEXT (PK) | Date in YYYYMMDD format |
| full_date | DATE | Date in YYYY-MM-DD format |
| day_of_week | INTEGER | 0=Monday, 6=Sunday |
| day_name | TEXT | Day name (Monday, Tuesday, etc.) |
| day_of_month | INTEGER | Day number (1-31) |
| day_of_year | INTEGER | Day of year (1-366) |
| week_of_year | INTEGER | ISO week number |
| month | INTEGER | Month number (1-12) |
| month_name | TEXT | Month name |
| quarter | INTEGER | Quarter (1-4) |
| year | INTEGER | Year |
| is_weekend | INTEGER | 1=Weekend, 0=Weekday |
| is_holiday | INTEGER | 1=Holiday, 0=Normal day |
| fiscal_year | INTEGER | Company fiscal year |
| fiscal_quarter | INTEGER | Company fiscal quarter |

---

## Transaction Tables (Facts)

### fact_purchase_orders
Purchase orders issued to suppliers.

| Field | Type | Description |
|-------|------|-------------|
| po_id | TEXT (PK) | Unique PO identifier |
| po_number | TEXT | PO number (format: PO-XXXXXXXX) |
| supplier_id | TEXT (FK) | Reference to dim_supplier |
| product_id | TEXT (FK) | Reference to dim_product |
| quantity | INTEGER | Ordered quantity |
| unit_cost | REAL | Cost per unit |
| total_cost | REAL | quantity × unit_cost |
| order_date | DATE | Date PO was created |
| expected_receipt_date | DATE | Expected delivery date |
| actual_receipt_date | DATE | Actual delivery date |
| status | TEXT | PENDING, COMPLETED, CANCELLED |
| created_by | TEXT | User who created PO |

**Status Logic:**
- PENDING: Awaiting delivery
- COMPLETED: Goods received
- CANCELLED: Order cancelled

---

### fact_goods_receipts
Records of inventory received into warehouses.

| Field | Type | Description |
|-------|------|-------------|
| receipt_id | TEXT (PK) | Unique receipt identifier |
| receipt_number | TEXT | Receipt number (format: GR-XXXXXXXX) |
| po_id | TEXT (FK) | Reference to fact_purchase_orders |
| receipt_date | DATE | Date goods received |
| quantity_received | INTEGER | Quantity received |
| warehouse_id | TEXT (FK) | Reference to dim_warehouse |
| quality_check_passed | INTEGER | 1=Passed, 0=Failed |
| notes | TEXT | Additional notes |

---

### fact_crm_leads
Potential customer leads from various sources.

| Field | Type | Description |
|-------|------|-------------|
| lead_id | TEXT (PK) | Unique lead identifier |
| lead_number | TEXT | Lead number (format: LEAD-XXXXXXXX) |
| customer_id | TEXT (FK) | Reference to dim_customer |
| salesperson_id | TEXT (FK) | Reference to dim_salesperson |
| estimated_value | REAL | Estimated deal value |
| lead_date | DATE | Date lead was created |
| lead_status | TEXT | NEW, CONTACTED, QUALIFIED, CONVERTED, LOST |
| source | TEXT | Lead source |
| notes | TEXT | Additional notes |

**Conversion Funnel:**
- Leads → Quotations: ~40% conversion
- Quotations → Sales Orders: ~40% conversion

---

### fact_sales_quotations
Formal price quotes provided to customers.

| Field | Type | Description |
|-------|------|-------------|
| quotation_id | TEXT (PK) | Unique quotation identifier |
| quotation_number | TEXT | Quotation number (format: QUO-XXXXXXXX) |
| lead_id | TEXT (FK) | Optional reference to fact_crm_leads |
| customer_id | TEXT (FK) | Reference to dim_customer |
| salesperson_id | TEXT (FK) | Reference to dim_salesperson |
| amount | REAL | Total quotation amount |
| quotation_date | DATE | Date quote was created |
| valid_until_date | DATE | Quote expiration date |
| status | TEXT | DRAFT, SENT, ACCEPTED, REJECTED, EXPIRED |
| notes | TEXT | Additional notes |

---

### fact_sales_orders
Customer purchase orders.

| Field | Type | Description |
|-------|------|-------------|
| so_id | TEXT (PK) | Unique SO identifier |
| so_number | TEXT | SO number (format: SO-XXXXXXXX) |
| customer_id | TEXT (FK) | Reference to dim_customer |
| product_id | TEXT (FK) | Reference to dim_product |
| quantity | INTEGER | Ordered quantity |
| unit_price | REAL | Selling price per unit |
| total_amount | REAL | quantity × unit_price |
| order_date | DATE | Date order was placed |
| expected_delivery_date | DATE | Expected delivery date |
| actual_delivery_date | DATE | Actual delivery date |
| status | TEXT | CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED |
| salesperson_id | TEXT (FK) | Reference to dim_salesperson |
| warehouse_id | TEXT (FK) | Reference to dim_warehouse |
| so_type | TEXT | STANDARD, RUSH, etc. |
| notes | TEXT | Additional notes |

**Status Flow:**
CONFIRMED → PROCESSING → SHIPPED → DELIVERED
                                      ↓
                                 CANCELLED

---

### fact_delivery_orders
Records of shipments to customers.

| Field | Type | Description |
|-------|------|-------------|
| delivery_id | TEXT (PK) | Unique delivery identifier |
| delivery_number | TEXT | Delivery number (format: DO-XXXXXXXX) |
| so_id | TEXT (FK) | Reference to fact_sales_orders |
| delivery_date | DATE | Date of delivery |
| quantity_delivered | INTEGER | Quantity delivered |
| warehouse_id | TEXT (FK) | Reference to dim_warehouse |
| driver_name | TEXT | Delivery driver |
| vehicle_number | TEXT | Vehicle registration |
| notes | TEXT | Additional notes |

---

### fact_customer_invoices
Billing documents sent to customers.

| Field | Type | Description |
|-------|------|-------------|
| invoice_id | TEXT (PK) | Unique invoice identifier |
| invoice_number | TEXT | Invoice number (format: INV-XXXXXXXX) |
| so_id | TEXT (FK) | Reference to fact_sales_orders |
| invoice_date | DATE | Invoice date |
| due_date | DATE | Payment due date |
| total_amount | REAL | Invoice total |
| amount_paid | REAL | Amount paid to date |
| status | TEXT | OPEN, PARTIAL, PAID, OVERDUE |
| payment_terms_days | INTEGER | Days until due |

**Aging Buckets:**
- CURRENT: Not yet due
- 1-30 DAYS: Due in 1-30 days
- 31-60 DAYS: 31-60 days overdue
- 61-90 DAYS: 61-90 days overdue
- OVER 90 DAYS: More than 90 days overdue

---

### fact_customer_payments
Customer payment records.

| Field | Type | Description |
|-------|------|-------------|
| payment_id | TEXT (PK) | Unique payment identifier |
| payment_number | TEXT | Payment number (format: PAY-XXXXXXXX) |
| invoice_id | TEXT (FK) | Reference to fact_customer_invoices |
| payment_date | DATE | Date payment received |
| amount_paid | REAL | Payment amount |
| payment_method | TEXT | Wire Transfer, Credit Card, Check, ACH, Cash |
| reference_number | TEXT | Payment reference |
| notes | TEXT | Additional notes |

---

### fact_inventory_ledger
Detailed inventory movement tracking.

| Field | Type | Description |
|-------|------|-------------|
| movement_id | INTEGER (PK) | Auto-increment ID |
| product_id | TEXT (FK) | Reference to dim_product |
| warehouse_id | TEXT (FK) | Reference to dim_warehouse |
| movement_date | DATE | Date of movement |
| movement_type | TEXT | GOODS_RECEIPT, DELIVERY |
| reference_type | TEXT | Source document type |
| reference_id | TEXT | Source document ID |
| quantity_in | INTEGER | Quantity received (0 for deliveries) |
| quantity_out | INTEGER | Quantity shipped (0 for receipts) |
| unit_cost | REAL | Cost at time of receipt |
| running_balance | INTEGER | Current inventory balance |

**Movement Types:**
- GOODS_RECEIPT: Inventory increase from supplier
- DELIVERY: Inventory decrease from sales

---

### fact_current_inventory
Current inventory snapshot.

| Field | Type | Description |
|-------|------|-------------|
| product_id | TEXT (FK) | Reference to dim_product |
| warehouse_id | TEXT (FK) | Reference to dim_warehouse |
| quantity_on_hand | INTEGER | Current quantity |
| average_cost | REAL | Average unit cost |
| last_updated | DATE | Last update timestamp |

---

### fact_sales_profitability
Calculated profit metrics per sales order.

| Field | Type | Description |
|-------|------|-------------|
| profitability_id | INTEGER (PK) | Auto-increment ID |
| so_id | TEXT (FK) | Reference to fact_sales_orders |
| product_id | TEXT (FK) | Reference to dim_product |
| quantity_sold | INTEGER | Quantity sold |
| revenue | REAL | Sales revenue |
| cost_of_goods_sold | REAL | Actual cost from inventory |
| gross_profit | REAL | revenue - cogs |
| gross_margin_pct | REAL | (gross_profit / revenue) × 100 |
| calculation_date | DATE | Date calculated |

---

## Analytics Tables

### analytics_fact_sales
Aggregated sales data with dimensions.

| Key Fields | Description |
|------------|-------------|
| Date Dimensions | year, month, quarter, fiscal_year |
| Customer Dimensions | customer_id, customer_name, industry, region |
| Product Dimensions | product_id, product_name, category |
| Sales Metrics | quantity, unit_price, total_revenue |
| Profit Metrics | cost_of_goods_sold, gross_profit, gross_margin_pct |

---

### analytics_fact_purchases
Aggregated purchase data with dimensions.

| Key Fields | Description |
|------------|-------------|
| Date Dimensions | year, month, quarter |
| Supplier Dimensions | supplier_id, supplier_name, country, supplier_type |
| Product Dimensions | product_id, product_name, category |
| Purchase Metrics | quantity, unit_cost, total_cost |
| Delivery Metrics | days_to_deliver, on_time_delivery |

---

### analytics_fact_inventory
Current inventory state with product details.

| Key Fields | Description |
|------------|-------------|
| Product Dimensions | product_id, product_name, sku, category |
| Warehouse Dimensions | warehouse_id, warehouse_name |
| Inventory Metrics | quantity_on_hand, average_cost, total_value |
| Activity Metrics | last_receipt_date, days_since_last_receipt |

---

### analytics_customer_performance
Customer-level aggregated metrics.

| Key Fields | Description |
|------------|-------------|
| Customer Dimensions | customer_id, customer_name, industry, region |
| Sales Metrics | total_orders, total_revenue, total_profit, avg_margin_pct |
| AR Metrics | total_invoices, open_invoices, overdue_invoices, avg_days_to_pay |
| Activity | last_order_date |

---

### analytics_product_performance
Product-level aggregated metrics.

| Key Fields | Description |
|------------|-------------|
| Product Dimensions | product_id, product_name, sku, category |
| Sales Metrics | units_sold, total_revenue, total_profit, avg_margin_pct |
| Purchase Metrics | total_purchases, avg_cost |
| Inventory | current_inventory |

---

### analytics_supplier_performance
Supplier-level aggregated metrics.

| Key Fields | Description |
|------------|-------------|
| Supplier Dimensions | supplier_id, supplier_name, country, supplier_type |
| Order Metrics | total_orders, total_spend |
| Performance Metrics | on_time_rate, avg_lead_time_days, product_variety |

---

### analytics_salesperson_performance
Salesperson-level aggregated metrics.

| Key Fields | Description |
|------------|-------------|
| Salesperson Dimensions | salesperson_id, salesperson_name, region |
| Lead Metrics | total_leads, converted_leads, conversion_rate |
| Sales Metrics | total_orders, total_revenue, avg_order_value |
| Profit Metrics | total_profit, avg_margin_pct |

---

### analytics_invoice_aging
Invoice aging analysis.

| Key Fields | Description |
|------------|-------------|
| Invoice Dimensions | invoice_id, invoice_number, so_number |
| Customer Dimensions | customer_id, customer_name |
| Date Dimensions | invoice_date, due_date |
| Amount Metrics | total_amount, amount_paid, amount_outstanding |
| Aging Metrics | days_overdue, aging_bucket, status |

---

### analytics_monthly_trends
Monthly aggregated metrics for trend analysis.

| Key Fields | Description |
|------------|-------------|
| Time Dimensions | year, month, month_name, fiscal_year, fiscal_quarter |
| Sales Metrics | total_sales_orders, total_revenue, total_cost, total_profit, avg_margin_pct |
| Customer Metrics | total_customers, total_products_sold |
| Purchase Metrics | total_purchase_orders, total_purchase_spend |
| Inventory | inventory_value |

---

## Data Relationships

### Procure-to-Pay Flow
```
dim_supplier → fact_purchase_orders → fact_goods_receipts → fact_inventory_ledger
                                                          ↓
dim_product ←─────────────────────────────────────────────────┘
```

### Order-to-Cash Flow
```
dim_customer ← fact_crm_leads → fact_sales_quotations → fact_sales_orders
                                                          ↓
dim_product →──────────────────────────────────────────────→ fact_sales_orders
                                                          ↓
fact_delivery_orders → fact_inventory_ledger
                       ↓
              fact_customer_invoices → fact_customer_payments
```

### Inventory Flow
```
fact_goods_receipts → fact_inventory_ledger (quantity_in)
                                                    ↓
fact_delivery_orders → fact_inventory_ledger (quantity_out)
                                                    ↓
                                          fact_current_inventory
```

### Costing Flow
```
fact_inventory_ledger (unit_cost) → fact_sales_profitability (cost_of_goods_sold)
fact_sales_orders (revenue) → fact_sales_profitability (revenue)
                                                    ↓
                                          gross_profit, gross_margin_pct
```

---

## Indexes

The following indexes are recommended for optimal query performance:

### Dimension Tables
- dim_product: category, sku
- dim_supplier: country, supplier_type
- dim_customer: industry, region
- dim_salesperson: region

### Transaction Tables
- fact_purchase_orders: supplier_id, product_id, order_date, status
- fact_goods_receipts: po_id, receipt_date
- fact_sales_orders: customer_id, product_id, order_date, status
- fact_delivery_orders: so_id, delivery_date
- fact_customer_invoices: so_id, due_date, status
- fact_customer_payments: invoice_id, payment_date
- fact_inventory_ledger: product_id, warehouse_id, movement_date

---

## Data Volume Summary

| Table | Record Count |
|-------|-------------|
| dim_product | 500 |
| dim_supplier | 100 |
| dim_customer | 1,000 |
| dim_salesperson | 20 |
| dim_warehouse | 3 |
| dim_date | 731 |
| fact_purchase_orders | 5,500 |
| fact_goods_receipts | 6,547 |
| fact_crm_leads | 3,000 |
| fact_sales_quotations | 2,000 |
| fact_sales_orders | 11,000 |
| fact_delivery_orders | 12,736 |
| fact_customer_invoices | 10,439 |
| fact_customer_payments | 6,242 |
| fact_inventory_ledger | 19,283 |
| fact_current_inventory | 1,150 |
| fact_sales_profitability | 4,419 |

---

*Generated for ERP Analytics Platform v1.0*
*Date Range: July 2023 - June 2025 (24 months)*