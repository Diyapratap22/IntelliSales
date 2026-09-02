# IntelliSales Project Context

## Project identity

**Title:** IntelliSales: AI Data Analyst for Sales Intelligence & Forecasting

**Domain:** Artificial Intelligence, Machine Learning, and Data Analytics

**Purpose:** Build a sales decision-support system that accepts CSV or Excel sales data, validates and profiles it, performs analytics and forecasting, and explains verified results through a natural-language interface and visualizations.

## Core principle

IntelliSales is **not a generic chatbot**. Calculations, analytics, and forecasts must come from deterministic Python or machine-learning pipelines. The AI layer interprets user questions, selects an appropriate tool, and explains verified results; it must not invent business numbers.

## Intended flow

```text
CSV / Excel upload
        -> data loading and validation
        -> data profiling and quality checks
        -> sales analytics and visualizations
        -> forecasting (when valid time-series data exists)
        -> natural-language explanation of verified results
```

## Current status — 2 September 2026

- Repository and virtual environment are set up.
- Automated profiling exists in `src/data_profiler.py`.
- Its initial automated test passes.
- `app/main.py`, `src/utils.py`, `src/forecasting.py`, and `src/agent.py` are placeholders for future milestones.
- No sample sales dataset is committed yet.

## Development rules

1. Build one small, tested feature at a time.
2. Keep functions focused and documented.
3. Add a test whenever practical.
4. Make small, meaningful Git commits with clear messages.
5. Do not expose API keys or commit `.env` files.
6. Prefer a finished, demonstrable core product over untested extra features.

## Delivery target

Finish a demonstrable project, synopsis, and presentation by **7 September 2026**. The project is the priority; documentation and slides should be based on the implemented system rather than promises.
