# ERP Analytics Platform

## AI-Powered Business Intelligence & Decision Support System

A comprehensive ERP analytics platform for a fictional distribution company. Features data exploration, executive dashboards, and an AI-powered decision support system.

---

## 🎯 Project Overview

This platform simulates a distribution company that:
- Purchases products from suppliers
- Receives inventory into warehouses
- Sells products to customers
- Ships products and issues invoices
- Receives customer payments

The system provides insights for **CEO**, **CFO**, **Operations Manager**, and **Business Analysts**.

---

## 📁 Project Structure

```
/workspace/AI-Projects/
├── database/
│   └── erp_database.db          # SQLite database (16MB, 28 tables)
├── data/                          # Generated CSV exports
├── scripts/                       # ETL and data generation scripts
├── output/                        # Reports and exports
├── docs/                          # Documentation & GitHub Pages redirect
├── templates/                     # Flask HTML templates
│   ├── base.html                  # Main layout with sidebar
│   ├── dashboard/                 # Analytics dashboard templates
│   │   ├── base.html
│   │   ├── executive.html
│   │   ├── sales.html
│   │   ├── purchasing.html
│   │   ├── inventory.html
│   │   └── aging.html
│   └── ai_advisor/                # AI Advisor templates
│       ├── index.html
│       ├── brief.html
│       ├── risks.html
│       └── opportunities.html
├── app.py                         # Main Flask application
├── dashboard_app.py                # Analytics dashboard routes
├── ai_advisor.py                   # AI Executive Advisor engine
└── README.md                       # This file
```

---

## 🔄 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ERP ANALYTICS PLATFORM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   Phase 1    │    │   Phase 2    │    │   Phase 3    │           │
│  │  Data Layer  │ →  │  Dashboard   │ →  │  AI Advisor  │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│        │                   │                    │                    │
│        ↓                   ↓                    ↓                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   SQLite     │    │  Chart.js    │    │Rule-Based    │           │
│  │  Database    │    │  Dashboards  │    │  Analytics   │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Data Generation (Faker)
         ↓
    SQLite Database
         ↓
┌────────┴────────┬────────┐
↓                 ↓        ↓
Dim Tables    Fact Tables  Analytics Tables
(Customers,     (Sales,     (Pre-computed
 Products,       Purchases,  aggregations
 Suppliers)       Inventory) for dashboards)
         ↓                 ↓
    ┌────────────────────────┐
    │    Flask Application   │
    └────────────────────────┘
              ↓
    ┌─────────┼─────────┬─────────┐
    ↓         ↓         ↓         ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Data   │ │Dash-   │ │ AI    │ │ SQL   │
│Explorer│ │boards  │ │Advisor │ │Query  │
└────────┘ └────────┘ └────────┘ └────────┘
```

---

## 📊 Phase 1: Database & Data Layer

### Database Schema (28 Tables)

#### Master Data Tables
| Table | Records | Description |
|-------|---------|-------------|
| `dim_product` | 500 | Product catalog with SKU, category, price |
| `dim_customer` | 1,000 | Customer information with industry, region |
| `dim_supplier` | 100 | Supplier details with country, type |
| `dim_salesperson` | 20 | Sales team members |
| `dim_warehouse` | 3 | Warehouse locations |
| `dim_date` | 730 | Date dimension for analytics |

#### Transaction Tables
| Table | Records | Description |
|-------|---------|-------------|
| `fact_crm_leads` | ~2,500 | Sales leads from CRM |
| `fact_sales_quotations` | ~1,500 | Sales quotations |
| `fact_sales_orders` | 10,439 | Sales order lines |
| `fact_delivery_orders` | ~9,000 | Delivery confirmations |
| `fact_customer_invoices` | ~9,000 | Customer invoices |
| `fact_customer_payments` | ~8,500 | Payment records |
| `fact_purchase_orders` | 5,500 | Purchase order lines |
| `fact_goods_receipts` | ~5,000 | Goods receiving |
| `fact_inventory_ledger` | ~50,000 | Inventory movements |

#### Analytics Tables (Pre-computed)
| Table | Description |
|-------|-------------|
| `analytics_fact_sales` | Sales with profit calculations |
| `analytics_fact_purchases` | Purchases with delivery metrics |
| `analytics_fact_inventory` | Current inventory snapshot |
| `analytics_monthly_trends` | Monthly aggregations (24 months) |
| `analytics_product_performance` | Product revenue/profit |
| `analytics_customer_performance` | Customer revenue/profit |
| `analytics_salesperson_performance` | Sales rep metrics |
| `analytics_supplier_performance` | Supplier spend/delivery |
| `analytics_invoice_aging` | AR aging analysis |

### Key Metrics Calculated

#### Sales Metrics
- **Revenue** = SUM(quantity × unit_price)
- **Cost of Goods Sold** = SUM(quantity × unit_cost) via FIFO
- **Gross Profit** = Revenue - COGS
- **Gross Margin %** = (Gross Profit / Revenue) × 100

#### Inventory Metrics
- **Inventory Value** = SUM(quantity × average_cost)
- **Slow-Moving** = Products with stock > 3× sales rate
- **Inventory Turnover** = COGS / Average Inventory

#### AR Metrics
- **Outstanding AR** = SUM(total_amount - amount_paid)
- **Overdue %** = (Overdue Amount / Outstanding AR) × 100
- **Days Overdue** = Current Date - Due Date

---

## 📈 Phase 2: Analytics Dashboards

### Dashboard URL: `/dashboard`

Five professional dashboards with Chart.js visualizations:

#### 1. Executive Dashboard (`/dashboard`)
**KPI Cards:**
- Total Revenue (12M)
- Gross Profit
- Gross Margin %
- Inventory Value
- Outstanding AR
- Outstanding AP
- Inventory Turnover

**Charts:**
- Revenue vs Profit trend (12 months)
- Sales Funnel (Leads → Quotations → Orders)

#### 2. Sales Analytics (`/dashboard/sales`)
- Monthly revenue bar chart
- Revenue by category (doughnut chart)
- Top customers horizontal bar chart
- Revenue by salesperson
- Top selling products table

#### 3. Purchasing Dashboard (`/dashboard/purchasing`)
- Monthly spend trend
- Spend by category pie chart
- Supplier performance table
- On-time delivery rate

#### 4. Inventory Dashboard (`/dashboard/inventory`)
- Inventory by warehouse (doughnut)
- Inventory by category (horizontal bar)
- Slow-moving products list
- Fast-moving products list

#### 5. AR/AP Aging (`/dashboard/aging`)
- AR aging stacked bar
- Aging trend line chart
- Invoice status donut
- Overdue invoices table
- Top overdue customers

---

## 🤖 Phase 3: AI Executive Advisor

### Advisor URL: `/ai-advisor`

**This is a Rule-Based Analytics Engine** - not machine learning. It applies business rules to your data to generate insights.

### How the Rules Work

#### 1. Executive Summary
Real-time KPI aggregation with trend calculation:

```
Revenue Change % = ((Current Month - Previous Month) / Previous Month) × 100
Margin % = (Gross Profit / Revenue) × 100
Slow Inventory % = (Slow Moving Count / Total Products) × 100
```

#### 2. Insight Engine Rules

| Insight | Trigger Rule |
|---------|--------------|
| Revenue Trend | `ABS(revenue_change) > 5%` |
| Margin Change | `ABS(margin_change) > 2pp` |
| Slow Inventory | `slow_moving_pct > 15%` |
| Overdue AR | `overdue_count > 0` |
| Customer Concentration | `top_customer_pct > 25%` |

#### 3. Risk Detection Rules

Each risk has a **score (0-100)** and **level**:

| Risk | Calculation | Threshold |
|------|-------------|-----------|
| **Customer Concentration** | `top_customer_pct × 2` | ≥50 = High |
| **Slow-Moving Inventory** | `slow_pct × 3` | >10% = High |
| **Overdue Receivables** | `critical_pct × 2` | ≥50 = High |
| **Supplier Dependency** | `top_supplier_pct × 2` | ≥50 = High |
| **Margin Compression** | `decline × 10` | >30 = High |

**Risk Levels:**
- Critical: Score ≥ 75
- High: Score 50-74
- Medium: Score 25-49
- Low: Score < 25

#### 4. Opportunity Detection Rules

| Opportunity | Rule |
|-------------|------|
| High-Growth Customer | `revenue > avg_revenue × 1.5` |
| Fast-Moving Product | `units_sold > avg_units_sold` |
| High-Margin Product | `margin > avg_margin × 1.2` |
| Efficient Supplier | `lead_time < avg_lead_time` |

#### 5. Recommendation Rules

Recommendations are triggered by detected issues:

| Issue | Recommended Actions |
|-------|---------------------|
| Slow inventory > 5 items | Launch promotions, reduce purchases, bundle products |
| Critical AR > 0 | Contact customers, escalate accounts, review credit terms |
| Margin declining > 5% | Review pricing, negotiate with suppliers, focus on high-margin products |
| Customer concentration > 30% | Develop upselling, increase marketing, diversify customer base |

#### 6. Forecasting Rules

Simple moving average with trend factor:

```
Forecast = (3-Month Moving Average) × (Trend Factor)
Trend Factor = (Last 3 Months Avg) / (Previous 3 Months Avg)

Confidence:
- 12+ months data: 90%
- 6-11 months data: 70%
- < 6 months data: 50%
```

#### 7. Daily Executive Brief

A snapshot combining:
- Top insight from data analysis
- Highest priority risk
- Most important recommendation

---

## 🧭 Navigation

### Data Explorer Module
| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Dashboard with KPI cards |
| Tables | `/tables` | Browse all 28 tables |
| Customers | `/customers` | Customer list |
| Suppliers | `/suppliers` | Supplier list |
| Products | `/products` | Product catalog |
| SQL Query | `/sql-query` | Run custom SELECT queries |
| Data Quality | `/data-quality` | Data validation checks |

### Dashboard Module
| Page | URL |
|------|-----|
| Executive | `/dashboard` |
| Sales | `/dashboard/sales` |
| Purchasing | `/dashboard/purchasing` |
| Inventory | `/dashboard/inventory` |
| AR/AP Aging | `/dashboard/aging` |

### AI Advisor Module
| Page | URL | Description |
|------|-----|-------------|
| AI Advisor | `/ai-advisor` | Main decision support page |
| Daily Brief | `/ai-advisor/brief` | Executive morning brief |
| Risks | `/ai-advisor/risks` | Detailed risk report |
| Opportunities | `/ai-advisor/opportunities` | Business opportunities |

---

## 🚀 Deployment

### Local Development

```bash
# Clone repository
git clone https://github.com/fwidianto/AI-Projects.git
cd AI-Projects

# Install dependencies
pip install flask faker pandas

# Set database path
export DATABASE_PATH=/path/to/database/erp_database.db

# Run application
python app.py

# Open http://localhost:5000
```

### PythonAnywhere Deployment

1. Create PythonAnywhere account
2. Clone repository:
   ```bash
   git clone https://github.com/fwidianto/AI-Projects.git
   ```
3. Install dependencies:
   ```bash
   pip install --user flask faker pandas
   ```
4. Set up web app in PythonAnywhere Web tab
5. Point to `app.py` as the WSGI file
6. Reload the web app

### GitHub Pages (Redirect Only)

The `docs/index.html` file creates a redirect page for GitHub Pages hosting.

To enable:
1. Go to repo Settings → Pages
2. Select Source: `main` branch, `/docs` folder
3. Your URL: `https://username.github.io/AI-Projects/`

---

## 📋 Sample Questions the Platform Can Answer

### Revenue Questions
- What is revenue by month? ✅
- What is revenue by customer? ✅
- What is revenue by product category? ✅
- What is revenue by salesperson? ✅
- What is the monthly trend? ✅

### Profitability Questions
- What is gross profit by product? ✅
- What is gross margin by category? ✅
- Which products have highest margin? ✅

### Inventory Questions
- What is current inventory value? ✅
- Which products are slow-moving? ✅
- Which products are fast-moving? ✅
- What inventory is aging? ✅

### AR/AP Questions
- What invoices are overdue? ✅
- What is the aging breakdown? ✅
- Which customers have most overdue? ✅
- What is total outstanding AR? ✅

### Risk Questions
- Are any customers at risk? ✅
- Is inventory too high? ✅
- Is margin declining? ✅
- Are suppliers reliable? ✅

### AI Advisor Questions
- What happened? ✅ (Executive Summary)
- Why did it happen? ✅ (Insight Engine)
- What risks exist? ✅ (Risk Detection)
- What opportunities exist? ✅ (Opportunity Engine)
- What should we do? ✅ (Recommendation Engine)
- What will happen next? ✅ (Forecasting)

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|------------|
| Database | SQLite |
| Backend | Flask (Python) |
| Frontend | HTML/CSS/JavaScript |
| Charts | Chart.js 4.4 |
| Data Generation | Faker |
| Data Processing | Pandas |

---

## 📄 License

MIT License - Feel free to use for educational purposes.

---

## 👤 Author

Built with OpenHands Agent on behalf of [@fwidianto](https://github.com/fwidianto)

---

*Last Updated: June 2026*