from __future__ import annotations

from datetime import datetime
from typing import Dict

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, relationship

from .database import Base

EMPLOYMENT_TYPES = ("FULL_TIME", "PART_TIME", "CONTRACT")
PAYROLL_STATUSES = ("OPEN", "PROCESSED", "PAID")


class TimestampMixin:
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = Column(String(255))

    employees = relationship("Employee", back_populates="department", cascade="all")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "employee_count": len(self.employees),
        }


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id: Mapped[int] = Column(Integer, primary_key=True)
    first_name: Mapped[str] = Column(String(80), nullable=False)
    last_name: Mapped[str] = Column(String(80), nullable=False)
    email: Mapped[str] = Column(String(120), unique=True, nullable=False)
    base_rate: Mapped[float] = Column(Numeric(10, 2), nullable=False)
    department_id: Mapped[int] = Column(ForeignKey("departments.id"), nullable=False)
    hire_date: Mapped[datetime] = Column(Date, nullable=False)
    employment_type: Mapped[str] = Column(Enum(*EMPLOYMENT_TYPES), nullable=False)

    department = relationship("Department", back_populates="employees")
    payroll_records = relationship(
        "PayrollRecord", back_populates="employee", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "base_rate": float(self.base_rate),
            "department": self.department.name if self.department else None,
            "department_id": self.department_id,
            "employment_type": self.employment_type,
            "hire_date": self.hire_date.isoformat(),
        }


class PayrollPeriod(Base, TimestampMixin):
    __tablename__ = "payroll_periods"

    id: Mapped[int] = Column(Integer, primary_key=True)
    label: Mapped[str] = Column(String(100), nullable=False, unique=True)
    start_date: Mapped[datetime] = Column(Date, nullable=False)
    end_date: Mapped[datetime] = Column(Date, nullable=False)
    status: Mapped[str] = Column(Enum(*PAYROLL_STATUSES), default="OPEN", nullable=False)

    records = relationship(
        "PayrollRecord", back_populates="payroll_period", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_period_dates"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "label": self.label,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
        }


class PayrollRecord(Base, TimestampMixin):
    __tablename__ = "payroll_records"

    id: Mapped[int] = Column(Integer, primary_key=True)
    employee_id: Mapped[int] = Column(ForeignKey("employees.id"), nullable=False)
    payroll_period_id: Mapped[int] = Column(
        ForeignKey("payroll_periods.id"), nullable=False
    )
    hours_worked: Mapped[float] = Column(Float, nullable=False)
    gross_pay: Mapped[float] = Column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[float] = Column(Numeric(12, 2), nullable=False)
    other_deductions: Mapped[float] = Column(Numeric(12, 2), default=0)
    net_pay: Mapped[float] = Column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = Column(Text)

    employee = relationship("Employee", back_populates="payroll_records")
    payroll_period = relationship("PayrollPeriod", back_populates="records")

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "payroll_period_id",
            name="uq_employee_period",
        ),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "employee": self.employee.to_dict() if self.employee else None,
            "employee_id": self.employee_id,
            "payroll_period_id": self.payroll_period_id,
            "period": self.payroll_period.to_dict()
            if self.payroll_period
            else None,
            "hours_worked": self.hours_worked,
            "gross_pay": float(self.gross_pay),
            "tax_amount": float(self.tax_amount),
            "other_deductions": float(self.other_deductions or 0),
            "net_pay": float(self.net_pay),
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

