-- ==================== DROP ALL TABLES ====================
DROP TABLE IF EXISTS inventory_count_item CASCADE;
DROP TABLE IF EXISTS inventory_count CASCADE;
DROP TABLE IF EXISTS invoice_item CASCADE;
DROP TABLE IF EXISTS invoice CASCADE;
DROP TABLE IF EXISTS sale CASCADE;
DROP TABLE IF EXISTS purchase CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- ==================== CREATE TABLES ====================

-- Users Table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Products Table
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(80) NOT NULL,
    cost_price FLOAT NOT NULL,
    sale_price FLOAT NOT NULL,
    min_stock INTEGER DEFAULT 5 NOT NULL,
    status VARCHAR(20) DEFAULT 'ativo' NOT NULL
);

-- Purchases Table
CREATE TABLE purchase (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product_code VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost FLOAT NOT NULL
);

-- Invoices Table
CREATE TABLE invoice (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    date DATE NOT NULL,
    total_amount FLOAT DEFAULT 0 NOT NULL,
    vendor_id INTEGER REFERENCES "user"(id)
);

-- Invoice Items Table
CREATE TABLE invoice_item (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL REFERENCES invoice(invoice_number),
    product_code VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price FLOAT NOT NULL,
    discount FLOAT DEFAULT 0 NOT NULL,
    subtotal FLOAT NOT NULL
);

-- Sales Table
CREATE TABLE sale (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product_code VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price FLOAT NOT NULL,
    vendor_id INTEGER REFERENCES "user"(id)
);

-- Inventory Count Table
CREATE TABLE inventory_count (
    id SERIAL PRIMARY KEY,
    count_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'em_progreso' NOT NULL,
    total_loss INTEGER DEFAULT 0 NOT NULL,
    total_variance INTEGER DEFAULT 0 NOT NULL,
    notes VARCHAR(500) DEFAULT '',
    user_id INTEGER REFERENCES "user"(id)
);

-- Inventory Count Items Table
CREATE TABLE inventory_count_item (
    id SERIAL PRIMARY KEY,
    inventory_count_id INTEGER NOT NULL REFERENCES inventory_count(id),
    product_code VARCHAR(50) NOT NULL,
    system_quantity INTEGER NOT NULL,
    physical_count INTEGER NOT NULL,
    variance INTEGER NOT NULL,
    variance_type VARCHAR(20) NOT NULL,
    loss_reason VARCHAR(50) DEFAULT '',
    notes VARCHAR(500) DEFAULT '',
    status VARCHAR(20) DEFAULT 'pendiente' NOT NULL
);

-- ==================== INSERT DEFAULT USERS ====================
INSERT INTO "user" (username, password, role) VALUES
('dev', 'scrypt:32768:8:1$5h5BNpWDwF6wHIG9$59bfeb78d2c243d742b048b8369daab9dc74b02de8a2950da088bce415ce1c16c1ab02e93c9bbb95934128b7deacb77d1668edf8636d0b735935cd3143f1cd14', 'dev'),
('admin', 'scrypt:32768:8:1$bFWIJTKLtwRAF2AX$23f98478b4d593578fc3c64b8a6b525ca6c407db01b4ecd30e4c69cf175b8eaf590a0d3a2ff4247f5b4aaa57ea628218f7df6a380b8956181e983497fbb75c74', 'admin'),
('vendedor', 'scrypt:32768:8:1$grsUojIyNmKwx6k9$011fbd699a4eaf3a1640230514cd643faa0badd69f19228328626ad628f3240e7a4b2657d941a9a9e1184feb769859523b6433945c4db3272540bdac9860403c', 'vendedor');

-- ==================== INDEXES ====================
CREATE INDEX idx_product_code ON product(code);
CREATE INDEX idx_purchase_product ON purchase(product_code);
CREATE INDEX idx_sale_product ON sale(product_code);
CREATE INDEX idx_sale_vendor ON sale(vendor_id);
CREATE INDEX idx_invoice_number ON invoice(invoice_number);
CREATE INDEX idx_invoice_vendor ON invoice(vendor_id);
CREATE INDEX idx_inventory_count_date ON inventory_count(count_date);

-- ==================== RESULTADO ====================
-- ✅ Tablas creadas: user, product, purchase, invoice, invoice_item, sale, inventory_count, inventory_count_item
-- ✅ Usuarios: dev (dev123), admin (admin123), vendedor (vendedor123)
-- ✅ Vendor tracking: sale.vendor_id y invoice.vendor_id con indexes
-- ✅ Indexes: 8 indices para performance
