from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.database import session_scope
from backend.models import Department, Employee

employees_bp = Blueprint("employees", __name__, url_prefix="/api/employees")


@employees_bp.get("")
def list_employees():
    search_term = request.args.get("q", "").lower()
    dept_filter = request.args.get("department_id")

    with session_scope() as session:
        stmt = select(Employee).order_by(Employee.last_name.asc())
        if dept_filter:
            stmt = stmt.where(Employee.department_id == int(dept_filter))
        employees = session.scalars(stmt).all()

        if search_term:
            employees = [
                emp
                for emp in employees
                if search_term in emp.full_name.lower()
                or search_term in emp.email.lower()
            ]

        return jsonify({"data": [emp.to_dict() for emp in employees]})


@employees_bp.post("")
def create_employee():
    payload = request.get_json(force=True)
    required_fields = [
        "first_name",
        "last_name",
        "email",
        "base_rate",
        "department_id",
        "employment_type",
        "hire_date",
    ]

    missing = [field for field in required_fields if field not in payload]
    if missing:
        return (
            jsonify({"error": f"Missing fields: {', '.join(missing)}"}),
            400,
        )

    try:
        hire_date = date.fromisoformat(payload["hire_date"])
    except ValueError:
        return jsonify({"error": "Invalid hire_date format, use YYYY-MM-DD"}), 400

    with session_scope() as session:
        department = session.get(Department, int(payload["department_id"]))
        if not department:
            return jsonify({"error": "Department not found"}), 404

        employee = Employee(
            first_name=payload["first_name"].strip(),
            last_name=payload["last_name"].strip(),
            email=payload["email"].strip().lower(),
            base_rate=float(payload["base_rate"]),
            department=department,
            employment_type=payload["employment_type"],
            hire_date=hire_date,
        )

        session.add(employee)
        try:
            session.flush()
        except IntegrityError:
            return jsonify({"error": "Email already exists"}), 409

        return jsonify({"message": "Employee created", "data": employee.to_dict()}), 201


@employees_bp.put("/<int:employee_id>")
def update_employee(employee_id: int):
    payload = request.get_json(force=True)

    with session_scope() as session:
        employee = session.get(Employee, employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        for field in ["first_name", "last_name", "email", "employment_type"]:
            if field in payload:
                setattr(employee, field, payload[field].strip())

        if "base_rate" in payload:
            employee.base_rate = float(payload["base_rate"])

        if "hire_date" in payload:
            try:
                employee.hire_date = date.fromisoformat(payload["hire_date"])
            except ValueError:
                return (
                    jsonify({"error": "Invalid hire_date format, use YYYY-MM-DD"}),
                    400,
                )

        if "department_id" in payload:
            department = session.get(Department, int(payload["department_id"]))
            if not department:
                return jsonify({"error": "Department not found"}), 404
            employee.department = department

        session.add(employee)

        return jsonify({"message": "Employee updated", "data": employee.to_dict()})


@employees_bp.delete("/<int:employee_id>")
def delete_employee(employee_id: int):
    with session_scope() as session:
        employee = session.get(Employee, employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        session.delete(employee)
        return jsonify({"message": "Employee removed"})

