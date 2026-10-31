INSERT INTO customers (full_name, email, city, created_at) VALUES
    ('Asha Patel', 'asha@example.test', 'Mumbai', '2025-01-10'),
    ('Ravi Shah', 'ravi@example.test', 'Pune', '2025-02-14'),
    ('Mina Das', 'mina@example.test', 'Kolkata', '2025-03-02'),
    ('Kabir Rao', 'kabir@example.test', 'Bengaluru', '2025-04-18'),
    ('Leela Nair', 'leela@example.test', 'Kochi', '2025-05-06'),
    ('Noah Sen', 'noah@example.test', 'Mumbai', '2025-06-21');

INSERT INTO products (product_name, category, unit_price) VALUES
    ('Notebook', 'Stationery', 4.50),
    ('Desk Lamp', 'Home', 28.00),
    ('Water Bottle', 'Outdoors', 16.75),
    ('Pen Set', 'Stationery', 8.25),
    ('Backpack', 'Outdoors', 42.00);

INSERT INTO orders (customer_id, product_id, quantity, ordered_at, status) VALUES
    (1, 1, 3, '2025-07-01', 'delivered'),
    (1, 2, 1, '2025-07-03', 'shipped'),
    (2, 3, 2, '2025-07-04', 'delivered'),
    (2, 4, 1, '2025-07-08', 'cancelled'),
    (3, 1, 5, '2025-07-10', 'delivered'),
    (3, 5, 1, '2025-07-12', 'pending'),
    (4, 2, 2, '2025-07-15', 'delivered'),
    (4, 3, 1, '2025-07-18', 'shipped'),
    (5, 4, 4, '2025-07-20', 'delivered'),
    (6, 5, 2, '2025-07-22', 'pending'),
    (6, 1, 2, '2025-07-24', 'delivered');
