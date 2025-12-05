from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.database import session_scope
from backend.models import Department

departments_bp = Blueprint("departments", __name__, url_prefix="/api/departments")


@departments_bp.get("")
def list_departments():
    with session_scope() as session:
        departments = session.scalars(select(Department).order_by(Department.name)).all()
        return jsonify({"data": [dept.to_dict() for dept in departments]})


@departments_bp.post("")
def create_department():
    payload = request.get_json(force=True)
    name = payload.get("name", "").strip()
    if not name:
        return jsonify({"error": "Department name is required"}), 400

    description = payload.get("description")

    with session_scope() as session:
        department = Department(name=name, description=description)
        session.add(department)
        try:
            session.flush()
        except IntegrityError:
            return jsonify({"error": "Department already exists"}), 409

        return (
            jsonify({"message": "Department created", "data": department.to_dict()}),
            201,
        )

