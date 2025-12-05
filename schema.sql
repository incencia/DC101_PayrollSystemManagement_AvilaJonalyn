-- Database schema for Payroll System Management
CREATE DATABASE IF NOT EXISTS payroll_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payroll_db;

DROP TABLE IF EXISTS payroll_records;
DROP TABLE IF EXISTS payroll_periods;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    base_rate DECIMAL(10,2) NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    employment_type ENUM('FULL_TIME','PART_TIME','CONTRACT') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_department FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE payroll_periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(100) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('OPEN','PROCESSED','PAID') DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_dates CHECK (end_date >= start_date)
);

CREATE TABLE payroll_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    payroll_period_id INT NOT NULL,
    hours_worked FLOAT NOT NULL,
    gross_pay DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL,
    other_deductions DECIMAL(12,2) DEFAULT 0,
    net_pay DECIMAL(12,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_employee_period (employee_id, payroll_period_id),
    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES employees(id),
    CONSTRAINT fk_period FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods(id)
);

-- Sample data
INSERT INTO departments (name, description)
VALUES ('Finance', 'Budgeting and reporting'),
       ('Human Resources', 'People operations and payroll'),
       ('Engineering', 'Product development');

INSERT INTO employees (first_name, last_name, email, base_rate, department_id, hire_date, employment_type)
VALUES ('Ava', 'Lopez', 'ava.lopez@example.com', 420, 3, '2022-03-14', 'FULL_TIME'),
       ('Noah', 'Garcia', 'noah.garcia@example.com', 380, 1, '2021-09-02', 'FULL_TIME'),
       ('Mia', 'Santos', 'mia.santos@example.com', 280, 2, '2023-01-05', 'PART_TIME');

INSERT INTO payroll_periods (label, start_date, end_date, status)
VALUES ('Week 48 - 2025', '2025-11-24', '2025-11-30', 'PROCESSED');

INSERT INTO payroll_records (employee_id, payroll_period_id, hours_worked, gross_pay, tax_amount, other_deductions, net_pay, notes)
VALUES (1, 1, 40, 16800, 3360, 500, 12940, 'Includes gadget allowance'),
       (2, 1, 38, 14440, 2888, 300, 11252, 'Standard payout');

