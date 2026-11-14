INSERT INTO departments (department_name) VALUES ('Engineering'), ('Sales'), ('Support');
INSERT INTO employees (department_id, full_name, city, hired_on) VALUES
    (1, 'Asha Patel', 'Mumbai', '2024-01-15'), (2, 'Ravi Shah', 'Pune', '2024-02-10'),
    (1, 'Mina Das', 'Kolkata', '2024-03-20'), (3, 'Kabir Rao', 'Bengaluru', '2024-04-25'),
    (2, 'Leela Nair', 'Kochi', '2024-05-30');
INSERT INTO projects (project_name, budget) VALUES ('Apollo', 100000), ('Beacon', 75000), ('Comet', 50000);
INSERT INTO employee_projects (employee_id, project_id, hours) VALUES
    (1, 1, 120), (1, 2, 80), (2, 2, 100), (3, 1, 90),
    (3, 3, 60), (4, 3, 110), (5, 2, 70);
