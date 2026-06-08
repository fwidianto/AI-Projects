# ERP Analytics Platform - Data Explorer

A professional web interface for browsing, searching, filtering, validating, and inspecting ERP data.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install flask faker pandas
```

### 2. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

---

## 📊 Features

### Home Dashboard
- Total Products, Customers, Suppliers
- Total Sales Orders, Invoices, Payments
- Total Inventory Value
- Recent Sales Orders
- Monthly Revenue Trend

### Table Explorer
Browse all 18 database tables with:
- **Pagination** - Navigate large datasets
- **Search** - Find records quickly
- **Sorting** - Click column headers to sort
- **CSV Export** - Download data for analysis

### Record Detail Pages
- **Customer Detail** - Sales history, invoices, payments, profitability
- **Supplier Detail** - Purchase orders, goods receipts, spend analysis
- **Product Detail** - Purchase history, sales history, inventory movements, margin analysis

### Data Quality Dashboard
Validate data integrity with checks for:
- Negative inventory
- Missing foreign keys
- Duplicate records
- Unpaid invoices
- Overdue invoices
- Inventory anomalies

### SQL Query Interface
- Run custom SELECT queries
- Read-only security (no INSERT/UPDATE/DELETE)
- Quick example queries
- Table reference sidebar

---

## 🗄️ Database Schema

### Master Data Tables

| Table | Records | Description |
|-------|---------|-------------|
| dim_product | 500 | Product catalog |
| dim_supplier | 100 | Supplier directory |
| dim_customer | 1,000 | Customer list |
| dim_salesperson | 20 | Sales team |
| dim_warehouse | 3 | Warehouse locations |

### Transaction Tables

| Table | Records | Description |
|-------|---------|-------------|
| fact_purchase_orders | 5,500 | Supplier orders |
| fact_goods_receipts | 6,547 | Inventory receipts |
| fact_sales_orders | 11,000 | Customer orders |
| fact_delivery_orders | 12,736 | Shipments |
| fact_customer_invoices | 10,439 | Billing |
| fact_customer_payments | 6,242 | Payments received |

### Analytics Tables

| Table | Description |
|-------|-------------|
| analytics_fact_sales | Sales with all dimensions |
| analytics_fact_purchases | Purchases with delivery metrics |
| analytics_fact_inventory | Current inventory state |
| analytics_customer_performance | Customer metrics + AR |
| analytics_product_performance | Product sales/purchase metrics |
| analytics_supplier_performance | Supplier on-time rate |
| analytics_salesperson_performance | Lead conversion, revenue |
| analytics_invoice_aging | AR aging buckets |
| analytics_monthly_trends | Monthly aggregates |

---

## 🔧 Technology Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Generation**: Faker, Pandas

---

## 📁 Project Structure

```
/workspace/AI-Projects/
├── app.py                      # Flask application
├── templates/                  # HTML templates
│   ├── base.html              # Base layout with sidebar
│   ├── index.html             # Dashboard
│   ├── tables.html            # Table explorer
│   ├── table_view.html        # Table data view
│   ├── customer_detail.html   # Customer detail page
│   ├── supplier_detail.html   # Supplier detail page
│   ├── product_detail.html    # Product detail page
│   ├── data_quality.html      # Data quality dashboard
│   ├── sql_query.html         # SQL query interface
│   └── error.html             # Error page
├── database/
│   └── erp_database.db        # SQLite database
├── data/                      # Raw CSV exports
├── output/                     # Analytics CSV exports
├── scripts/
│   ├── generate_erp_data.py   # Data generator
│   └── run_etl.py             # ETL pipeline
└── docs/
    ├── README.md              # This file
    ├── data_dictionary.md     # Table specifications
    └── erd.md                 # Entity relationship diagram
```

---

## 🔒 Security

The SQL Query interface is **read-only**:
- ✅ SELECT queries allowed
- ❌ INSERT, UPDATE, DELETE blocked
- ❌ DROP, ALTER, CREATE blocked
- Multiple statements prevented

---

## 📈 Business Questions Answerable

| Question | Table/Route |
|----------|-------------|
| What is revenue by month? | analytics_monthly_trends |
| What is gross profit by product? | analytics_product_performance |
| Which customers are most profitable? | analytics_customer_performance |
| Which suppliers provide best margins? | analytics_supplier_performance |
| What inventory is aging? | analytics_fact_inventory |
| Which invoices are overdue? | analytics_invoice_aging |

---

## 📝 License

This project is for demonstration and development purposes.

---

*ERP Analytics Platform v2.0 - Data Explorer*
