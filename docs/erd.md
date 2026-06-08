# ERP Analytics Platform - Entity Relationship Diagram

## Diagram Legend

```
┌─────────────────────┐
│    DIMENSION        │  Master/Reference data tables
│    (Yellow)         │
└─────────────────────┘

┌─────────────────────┐
│    TRANSACTION      │  Operational fact tables
│    (Blue)           │
└─────────────────────┘

┌─────────────────────┐
│    ANALYTICS        │  Aggregated tables
│    (Green)          │
└─────────────────────┘

┌─────────┐     ┌─────────┐
│   PK    │     │   FK    │  Primary/Foreign keys
└─────────┘     └─────────┘
```

---

## Master Data Layer (Dimension Tables)

```
┌──────────────────────────────┐
│        dim_product           │
├──────────────────────────────┤
│ PK product_id                │
│      sku                     │
│      product_name            │
│      category                 │
│      default_selling_price   │
│      unit_cost               │
│      is_active               │
└──────────────────────────────┘
           │
           │ 1:M
           ↓
┌──────────────────────────────┐
│     fact_purchase_orders     │
├──────────────────────────────┤
│ PK po_id                     │
│      po_number              │
│ FK supplier_id ──────────────┼──────────┐
│ FK product_id ──────────────┘          │
│      quantity                          │
│      unit_cost                         │
│      total_cost                        │
│      order_date                        │
│      expected_receipt_date             │
│      actual_receipt_date              │
│      status                            │
└────────────────────────────────────────┘
           │
           │ 1:M
           ↓
┌──────────────────────────────┐
│     fact_goods_receipts      │
├──────────────────────────────┤
│ PK receipt_id                │
│      receipt_number          │
│ FK po_id ────────────────────┤
│      receipt_date            │
│      quantity_received       │
│ FK warehouse_id ────────────┼─┐
│      quality_check_passed    │ │
│      notes                   │ │
└──────────────────────────────┘ │
                                 │
┌──────────────────────────────┐ │
│       dim_warehouse          │ │
├──────────────────────────────┤ │
│ PK warehouse_id              │ │
│      warehouse_name          │ │
│      location                │ │
│      capacity                │ │
│      manager_name            │ │
└──────────────────────────────┘ │
                                 │
                                 ↓
┌──────────────────────────────────────────────┐
│            fact_inventory_ledger             │
├──────────────────────────────────────────────┤
│ PK movement_id                               │
│ FK product_id ───────────────────────────────┤
│ FK warehouse_id ─────────────────────────────┤
│      movement_date                            │
│      movement_type (GOODS_RECEIPT/DELIVERY)  │
│      reference_type                           │
│      reference_id                             │
│      quantity_in                              │
│      quantity_out                             │
│      unit_cost                                │
│      running_balance                          │
└──────────────────────────────────────────────┘
           │
           │ Aggregation
           ↓
┌──────────────────────────────┐
│   fact_current_inventory     │
├──────────────────────────────┤
│ PK product_id                │
│ PK warehouse_id              │
│      quantity_on_hand        │
│      average_cost            │
│      last_updated            │
└──────────────────────────────┘
```

---

## Order to Cash Flow

```
┌──────────────────────────────┐
│       dim_customer            │
├──────────────────────────────┤
│ PK customer_id               │
│      customer_name           │
│      industry                │
│      region                  │
│      country                 │
│      credit_limit            │
│      payment_terms_days      │
│      is_active               │
└──────────────────────────────┘
           │
           │ 1:M
           ↓
┌──────────────────────────────┐
│       fact_crm_leads         │
├──────────────────────────────┤
│ PK lead_id                   │
│      lead_number            │
│ FK customer_id ──────────────┤
│ FK salesperson_id ───────────┼─┐
│      estimated_value         │ │
│      lead_date              │ │
│      lead_status            │ │
│      source                 │ │
│      notes                  │ │
└──────────────────────────────┘ │
                                 │
┌──────────────────────────────┐ │
│     dim_salesperson          │ │
├──────────────────────────────┤ │
│ PK salesperson_id            │ │
│      first_name              │ │
│      last_name              │ │
│      email                  │ │
│      phone                  │ │
│      region                 │ │
│      hire_date              │ │
└──────────────────────────────┘ │
                                 │
                                 ↓
┌──────────────────────────────┐
│   fact_sales_quotations      │
├──────────────────────────────┤
│ PK quotation_id              │
│      quotation_number        │
│ FK lead_id ──────────────────┤
│ FK customer_id               │
│ FK salesperson_id             │
│      amount                  │
│      quotation_date          │
│      valid_until_date        │
│      status                  │
│      notes                   │
└──────────────────────────────┘
           │
           │ 1:M
           ↓
┌──────────────────────────────────────────────┐
│            fact_sales_orders                 │
├──────────────────────────────────────────────┤
│ PK so_id                                     │
│      so_number                               │
│ FK customer_id ──────────────────────────────┤
│ FK product_id ────────────────────────────────┤
│      quantity                                │
│      unit_price                              │
│      total_amount                            │
│      order_date                              │
│      expected_delivery_date                 │
│      actual_delivery_date                   │
│      status                                  │
│ FK salesperson_id                           │
│ FK warehouse_id                             │
│      so_type                                 │
│      notes                                   │
└──────────────────────────────────────────────┘
           │
           │ 1:M
           ↓
┌──────────────────────────────┐
│   fact_delivery_orders      │
├──────────────────────────────┤
│ PK delivery_id              │
│      delivery_number        │
│ FK so_id ────────────────────┤
│      delivery_date          │
│      quantity_delivered     │
│ FK warehouse_id             │
│      driver_name            │
│      vehicle_number         │
│      notes                  │
└──────────────────────────────┘
           │
           │ Deducts from
           ↓
┌──────────────────────────────────────────────┐
│            fact_inventory_ledger             │
├──────────────────────────────────────────────┤
│ (See inventory section above)                 │
└──────────────────────────────────────────────┘
           │
           │ Costs calculated
           ↓
┌──────────────────────────────────────────────┐
│       fact_sales_profitability               │
├──────────────────────────────────────────────┤
│ PK profitability_id                          │
│ FK so_id ────────────────────────────────────┤
│ FK product_id ───────────────────────────────┤
│      quantity_sold                           │
│      revenue                                 │
│      cost_of_goods_sold                      │
│      gross_profit                            │
│      gross_margin_pct                        │
│      calculation_date                        │
└──────────────────────────────────────────────┘
           │
           │ 1:1
           ↓
┌──────────────────────────────┐
│  fact_customer_invoices     │
├──────────────────────────────┤
│ PK invoice_id               │
│      invoice_number         │
│ FK so_id ────────────────────┤
│      invoice_date           │
│      due_date               │
│      total_amount           │
│      amount_paid            │
│      status                 │
│      payment_terms_days     │
└──────────────────────────────┘
           │
           │ 1:M
           ↓
┌──────────────────────────────┐
│  fact_customer_payments      │
├──────────────────────────────┤
│ PK payment_id               │
│      payment_number         │
│ FK invoice_id ──────────────┤
│      payment_date           │
│      amount_paid             │
│      payment_method         │
│      reference_number        │
│      notes                  │
└──────────────────────────────┘
```

---

## Analytics Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    ANALYTICS TABLES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐   ┌─────────────────┐                 │
│  │ analytics_      │   │ analytics_      │                 │
│  │ fact_sales      │   │ fact_purchases  │                 │
│  ├─────────────────┤   ├─────────────────┤                 │
│  │ All dimensions  │   │ All dimensions  │                 │
│  │ + Sales metrics │   │ + Purchase mtrcs │                 │
│  │ + Profit metrics│   │ + Delivery mtrcs│                 │
│  └─────────────────┘   └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐   ┌─────────────────┐                 │
│  │ analytics_      │   │ analytics_      │                 │
│  │ fact_inventory  │   │ customer_       │                 │
│  ├─────────────────┤   │ performance     │                 │
│  │ Product dims    │   ├─────────────────┤                 │
│  │ Warehouse dims   │   │ Customer dims   │                 │
│  │ Inventory mtrcs  │   │ Sales + AR mtrcs│                 │
│  └─────────────────┘   └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐   ┌─────────────────┐                 │
│  │ analytics_      │   │ analytics_      │                 │
│  │ product_        │   │ supplier_       │                 │
│  │ performance     │   │ performance     │                 │
│  ├─────────────────┤   ├─────────────────┤                 │
│  │ Product dims    │   │ Supplier dims   │                 │
│  │ Sales metrics   │   │ Order + Perf    │                 │
│  │ Purchase metrics│   │ metrics         │                 │
│  └─────────────────┘   └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐   ┌─────────────────┐                 │
│  │ analytics_      │   │ analytics_      │                 │
│  │ salesperson_    │   │ invoice_aging   │                 │
│  │ performance     │   ├─────────────────┤                 │
│  ├─────────────────┤   │ Invoice dims    │                 │
│  │ Salesperson dims│   │ Amount metrics  │                 │
│  │ Lead + Sales    │   │ Aging metrics   │                 │
│  │ metrics         │   └─────────────────┘                 │
│  └─────────────────┘                                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          analytics_monthly_trends                  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Time dimensions (year, month, fiscal_year/quarter) │   │
│  │ Sales metrics (orders, revenue, cost, profit)      │   │
│  │ Purchase metrics (orders, spend)                   │   │
│  │ Inventory value                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Relationships Summary

| Parent Table | Child Table | Relationship | Type |
|--------------|-------------|--------------|------|
| dim_supplier | fact_purchase_orders | 1:M | Supplier → POs |
| dim_product | fact_purchase_orders | 1:M | Product → POs |
| dim_warehouse | fact_goods_receipts | 1:M | Warehouse → Receipts |
| fact_purchase_orders | fact_goods_receipts | 1:M | PO → Receipts |
| dim_customer | fact_crm_leads | 1:M | Customer → Leads |
| dim_salesperson | fact_crm_leads | 1:M | Salesperson → Leads |
| fact_crm_leads | fact_sales_quotations | 1:M | Lead → Quotations |
| dim_customer | fact_sales_orders | 1:M | Customer → SOs |
| dim_product | fact_sales_orders | 1:M | Product → SOs |
| fact_sales_orders | fact_delivery_orders | 1:M | SO → Deliveries |
| fact_sales_orders | fact_customer_invoices | 1:1 | SO → Invoice |
| fact_customer_invoices | fact_customer_payments | 1:M | Invoice → Payments |
| dim_product | fact_inventory_ledger | 1:M | Product → Movements |
| dim_warehouse | fact_inventory_ledger | 1:M | Warehouse → Movements |
| dim_product | fact_current_inventory | 1:M | Product → Current Stock |
| fact_sales_orders | fact_sales_profitability | 1:1 | SO → Profitability |

---

## Data Flow Summary

### Procure-to-Pay Flow
```
Supplier → PO → Goods Receipt → Inventory Ledger
                                ↓
                         Current Inventory
```

### Order-to-Cash Flow
```
Customer → Lead → Quotation → SO → Delivery → Invoice → Payment
               ↓              ↓        ↓
            Salesperson    Inventory  AR Aging
                             ↓
                        Profitability
```

---

*ERD Generated for ERP Analytics Platform v1.0*