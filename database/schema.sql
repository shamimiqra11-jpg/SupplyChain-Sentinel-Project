CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    country TEXT NOT NULL,
    product_category TEXT NOT NULL,
    contact_information TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    supplier_id INTEGER,
    unit_cost REAL NOT NULL DEFAULT 0,
    inventory_level INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);


CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_number TEXT NOT NULL UNIQUE,
    supplier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    expected_delivery TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    total_value REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);


CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    supplier_id INTEGER NOT NULL,

    risk_score REAL NOT NULL,

    risk_level TEXT NOT NULL,

    reliability REAL NOT NULL DEFAULT 0,

    geographic_risk REAL NOT NULL DEFAULT 0,

    financial_stability REAL NOT NULL DEFAULT 0,

    delivery_performance REAL NOT NULL DEFAULT 0,

    inventory_dependency REAL NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);


CREATE TABLE IF NOT EXISTS weather_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    supplier_id INTEGER NOT NULL,

    temperature REAL,

    apparent_temperature REAL,

    precipitation REAL,

    wind_speed REAL,

    weather_code INTEGER,

    weather_condition TEXT,

    weather_risk_score REAL,

    weather_risk_level TEXT,

    alert_message TEXT,

    latitude REAL,

    longitude REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);