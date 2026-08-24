# SupplyChain Sentinel AI

SupplyChain Sentinel AI is the foundation for an industrial AI-powered supply chain risk intelligence platform. This initial version focuses on a clean Python and Streamlit application architecture, SQLite persistence, and operational data management for suppliers, products, purchase orders, and future risk intelligence workflows.

## Current Capabilities

- Professional Streamlit enterprise dashboard shell
- Sidebar navigation for:
  - Dashboard
  - Suppliers
  - Products
  - Purchase Orders
  - Risk Intelligence
  - What-If Simulation
  - Settings
- SQLite database initialization and persistence
- Supplier management with add/view workflows
- Product management with supplier assignment and add/view workflows
- Purchase order management with add/view workflows
- Foundational schema for suppliers, products, purchase orders, and risk assessments
- Placeholder workspaces for future risk intelligence and simulation capabilities

## Project Structure

```text
.
├── app/                  # Future Streamlit page modules and app components
├── app.py                # Main Streamlit entry point
├── data/                 # SQLite database file is created here at runtime
├── database/             # Database connection and schema management
├── ml/                   # Reserved for future machine learning modules
├── models/               # Reserved for future domain/data models
├── nlp/                  # Reserved for future NLP modules
├── services/             # Application service layer for database operations
├── utils/                # Reserved for shared helpers
├── requirements.txt      # Python dependencies
└── README.md             # Setup and run instructions
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

The SQLite database is created automatically at `data/supplychain_sentinel.db` when the app starts.

## Development Notes

This foundation intentionally does not include machine learning, NLP, live weather, news APIs, or advanced prediction logic yet. Those capabilities can be added incrementally on top of the existing modular structure.


## Phase 2: Supplier Risk Intelligence

The platform includes an explainable, configurable weighted risk engine covering supplier reliability, geographic concentration, financial stability, delivery performance, and inventory dependency. Assessments are persisted in SQLite, with supplier history, latest risk register, risk distribution metrics, explanations, and recommended mitigation actions.

Current scoring is rules-based and intentionally prepared for future ML integration.


## Phase 3: Real-Time Weather Intelligence

Supplier locations can now be resolved to geographic coordinates and checked against live weather data. The platform calculates a 0–100 weather disruption risk score using temperature, apparent temperature, precipitation, wind speed, and severe weather conditions. Each assessment is stored in SQLite and displayed in a supplier weather risk register.

No API key is required for the current weather integration. Internet access is required when performing a live weather check.
