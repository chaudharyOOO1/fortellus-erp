from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_hr_or_admin, require_accounts_or_admin, require_owner
from app.core.database import get_db

router = APIRouter()

@router.get("/summary")
def erp_summary(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Owner/admin executive summary backed by the existing Supabase ERP tables."""
    def scalar(sql: str):
        return db.execute(text(sql)).scalar_one()
    return {
        "employees": scalar("select count(*) from employees"),
        "active_employees": scalar("select count(*) from employees where status = 'ACTIVE'"),
        "clients": scalar("select count(*) from clients"),
        "active_sites": scalar("select count(*) from sites where is_active = true"),
        "pending_salary": scalar("select count(*) from salary_records where lifecycle_status in ('DRAFT','CALCULATED')"),
        "open_salary_holds": scalar("select count(*) from salary_holds where status = 'HELD'"),
        "overdue_risks": scalar("select count(*) from risk_flags where resolved = false"),
        "unpaid_invoices": scalar("select count(*) from invoices where clearance_status <> 'PAID'"),
    }

@router.get("/employees")
def list_employees(
    status: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    site_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_hr_or_admin),
):
    sql = "select * from employees where 1=1"
    params = {}
    if status:
        sql += " and status = :status"; params["status"] = status
    if branch:
        sql += " and branch = :branch"; params["branch"] = branch
    if site_id is not None:
        sql += " and site_id = :site_id"; params["site_id"] = site_id
    sql += " order by created_at desc"
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]

@router.get("/compliance-expiry")
def compliance_expiry(
    days: int = Query(60, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_hr_or_admin),
):
    cutoff = date.today() + timedelta(days=days)
    rows = db.execute(text("""
        select d.*, e.employee_code, e.name
        from employee_documents d
        join employees e on e.id = d.employee_id
        where d.expiry_date is not null and d.expiry_date <= :cutoff
        order by d.expiry_date asc
    """), {"cutoff": cutoff}).mappings().all()
    return [dict(r) for r in rows]

@router.get("/payroll")
def payroll(month: Optional[str] = Query(None), db: Session = Depends(get_db), current_user=Depends(require_hr_or_admin)):
    sql = """
        select s.*, e.employee_code, e.name
        from salary_records s join employees e on e.id=s.employee_id
        where 1=1
    """
    params = {}
    if month:
        sql += " and s.month = :month"; params["month"] = month
    sql += " order by s.month desc, e.name"
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]

@router.get("/expenses")
def expenses(branch: Optional[str] = Query(None), client_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user=Depends(require_accounts_or_admin)):
    sql = "select * from expenses where 1=1"; params={}
    if branch: sql += " and branch=:branch"; params["branch"]=branch
    if client_id is not None: sql += " and client_id=:client_id"; params["client_id"]=client_id
    sql += " order by expense_date desc, created_at desc"
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]

@router.get("/risk-flags")
def risk_flags(db: Session = Depends(get_db), current_user=Depends(require_owner)):
    rows = db.execute(text("select * from risk_flags where resolved=false order by detected_at desc")).mappings().all()
    return [dict(r) for r in rows]
