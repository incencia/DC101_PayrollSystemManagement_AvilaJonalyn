from datetime import date

from sqlalchemy import func, select

from backend.database import init_db, session_scope
from backend.models import Department, Employee, PayrollPeriod, PayrollRecord


def seed():
    init_db()
    with session_scope() as session:
        existing_departments = session.scalar(select(func.count(Department.id)))
        if existing_departments:
            print("Database already seeded.")
            return

        departments = [
            Department(name="Finance", description="Budgeting and reporting"),
            Department(name="Human Resources", description="People operations"),
            Department(name="Engineering", description="Product development"),
        ]
        session.add_all(departments)
        session.flush()

        employees = [
            Employee(
                first_name="Ava",
                last_name="Lopez",
                email="ava.lopez@example.com",
                base_rate=420,
                department_id=departments[2].id,
                employment_type="FULL_TIME",
                hire_date=date(2022, 3, 14),
            ),
            Employee(
                first_name="Noah",
                last_name="Garcia",
                email="noah.garcia@example.com",
                base_rate=380,
                department_id=departments[0].id,
                employment_type="FULL_TIME",
                hire_date=date(2021, 9, 2),
            ),
            Employee(
                first_name="Mia",
                last_name="Santos",
                email="mia.santos@example.com",
                base_rate=280,
                department_id=departments[1].id,
                employment_type="PART_TIME",
                hire_date=date(2023, 1, 5),
            ),
        ]
        session.add_all(employees)
        session.flush()

        period = PayrollPeriod(
            label="Week 48 - 2025",
            start_date=date(2025, 11, 24),
            end_date=date(2025, 11, 30),
            status="PROCESSED",
        )
        session.add(period)
        session.flush()

        sample_records = [
            PayrollRecord(
                employee_id=employees[0].id,
                payroll_period_id=period.id,
                hours_worked=40,
                gross_pay=16800,
                tax_amount=3360,
                other_deductions=500,
                net_pay=12940,
                notes="Includes gadget allowance",
            ),
            PayrollRecord(
                employee_id=employees[1].id,
                payroll_period_id=period.id,
                hours_worked=38,
                gross_pay=14440,
                tax_amount=2888,
                other_deductions=300,
                net_pay=11252,
                notes="Standard payout",
            ),
        ]
        session.add_all(sample_records)

        print("Database seeded with demo data.")


if __name__ == "__main__":
    seed()

