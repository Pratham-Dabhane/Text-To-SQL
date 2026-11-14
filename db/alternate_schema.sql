CREATE TABLE departments (
    department_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE
);
CREATE TABLE employees (
    employee_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    full_name TEXT NOT NULL,
    city TEXT NOT NULL,
    hired_on DATE NOT NULL
);
CREATE TABLE projects (
    project_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_name TEXT NOT NULL UNIQUE,
    budget NUMERIC(12, 2) NOT NULL CHECK (budget >= 0)
);
CREATE TABLE employee_projects (
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
    project_id INTEGER NOT NULL REFERENCES projects(project_id),
    hours INTEGER NOT NULL CHECK (hours > 0),
    PRIMARY KEY (employee_id, project_id)
);
