# IntelliSales Sales Data Contract

This document defines the minimum structure IntelliSales expects from a sales dataset.

## Required columns

| Column | Meaning | Example | Rules |
|---|---|---|---|
| `date` | Date of the sale or order | `2026-01-15` | Must be a valid date. |
| `product` | Product name | `Laptop` | Must not be blank. |
| `region` | Sales region | `North` | Must not be blank. |
| `quantity` | Units sold | `3` | Must be a whole number greater than zero. |
| `unit_price` | Price for one unit | `55000.00` | Must be zero or greater. |
| `cost` | Total cost of the sale | `120000.00` | Must be zero or greater. |
| `category` *(optional)* | Product category | `Computing` | If present, must not be blank. If absent, it is derived from `product`. |

## Derived business metrics

```text
revenue = quantity × unit_price
profit = revenue − cost