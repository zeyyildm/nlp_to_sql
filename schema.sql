-- Eğer önceden kalan hatalı tablolar varsa temizleyelim
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- 1. Müşteriler Tablosu
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at DATE
);

-- 2. Ürünler Tablosu
-- 2. Ürünler Tablosu
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 3. Siparişler Tablosu
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    total_amount NUMERIC(10, 2),
    created_at DATE
);

-- 4. Sipariş Detayları Tablosu
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
);