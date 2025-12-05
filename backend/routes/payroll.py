from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select

from backend.database import session_scope
from backend.models import Department, Employee, PayrollPeriod, PayrollRecord

payroll_bp = Blueprint("payroll", __name__)


@payroll_bp.get("/api/payroll-records")
def list_payroll_records():
    employee_id = request.args.get("employee_id")
    period_id = request.args.get("period_id")

    with session_scope() as session:
        stmt = select(PayrollRecord).order_by(PayrollRecord.created_at.desc())
        if employee_id:
            stmt = stmt.where(PayrollRecord.employee_id == int(employee_id))
        if period_id:
            stmt = stmt.where(PayrollRecord.payroll_period_id == int(period_id))

        records = session.scalars(stmt).unique().all()
        return jsonify({"data": [record.to_dict() for record in records]})


@payroll_bp.get("/api/payroll-periods")
def list_periods():
    with session_scope() as session:
        periods = session.scalars(
            select(PayrollPeriod).order_by(PayrollPeriod.start_date.desc())
        ).all()
        return jsonify({"data": [period.to_dict() for period in periods]})


@payroll_bp.post("/api/payroll-records")
def create_payroll_record():
    payload = request.get_json(force=True)
    required = [
        "employee_id",
        "period_label",
        "period_start",
        "period_end",
        "hours_worked",
        "tax_rate",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        start_date = date.fromisoformat(payload["period_start"])
        end_date = date.fromisoformat(payload["period_end"])
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    if end_date < start_date:
        return jsonify({"error": "End date must be after start date"}), 400

    hours_worked = float(payload["hours_worked"])
    tax_rate = float(payload["tax_rate"])
    if hours_worked <= 0:
        return jsonify({"error": "Hours worked must be greater than zero"}), 400
    if not 0 <= tax_rate <= 1:
        return jsonify({"error": "Tax rate must be between 0 and 1"}), 400
    hourly_rate = float(payload.get("hourly_rate", 0))
    deductions = float(payload.get("other_deductions", 0))
    notes = payload.get("notes")

    with session_scope() as session:
        employee = session.get(Employee, payload["employee_id"])
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        if hourly_rate <= 0:
            hourly_rate = float(employee.base_rate)

        period = (
            session.execute(
                select(PayrollPeriod).where(PayrollPeriod.label == payload["period_label"])
            )
            .scalars()
            .first()
        )
        if not period:
            period = PayrollPeriod(
                label=payload["period_label"],
                start_date=start_date,
                end_date=end_date,
            )
            session.add(period)
            session.flush()

        gross_pay = hours_worked * hourly_rate
        tax_amount = gross_pay * tax_rate
        net_pay = gross_pay - tax_amount - deductions

        record = PayrollRecord(
            employee=employee,
            payroll_period=period,
            hours_worked=hours_worked,
            gross_pay=gross_pay,
            tax_amount=tax_amount,
            other_deductions=deductions,
            net_pay=net_pay,
            notes=notes,
        )
        session.add(record)
        session.flush()

        return (
            jsonify({"message": "Payroll recorded", "data": record.to_dict()}),
            201,
        )


@payroll_bp.get("/api/summary")
def payroll_summary():
    """Provide aggregate data for the dashboard cards."""
    with session_scope() as session:
        total_employees = session.scalar(select(func.count(Employee.id))) or 0
        total_departments = session.scalar(select(func.count(Department.id))) or 0
        total_payroll = session.scalar(
            select(func.coalesce(func.sum(PayrollRecord.net_pay), 0))
        ) or 0
        processed_periods = session.scalar(select(func.count(PayrollPeriod.id))) or 0

        return jsonify(
            {
                "totalEmployees": total_employees,
                "totalDepartments": total_departments,
                "totalNetPay": float(total_payroll or 0),
                "periods": processed_periods,
            }
        )

