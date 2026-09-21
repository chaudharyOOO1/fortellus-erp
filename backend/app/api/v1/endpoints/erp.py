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
        "active_employees": scalar("select count(*) from employees where lower(status) = 'active'"),
        "clients": scalar("select count(*) from clients"),
        "active_sites": scalar("select count(*) from sites where is_active = true"),
        "salary_records": scalar("select count(*) from salary_records"),
        "pending_salary": scalar("select count(*) from salary_records where lifecycle_status in ('DRAFT','CALCULATED')"),
        "open_salary_holds": scalar("select count(*) from salary_holds where status = 'HELD'"),
        "open_risks": scalar("select count(*) from risk_flags where resolved = false"),
        "unpaid_invoices": scalar("select count(*) from invoices where clearance_status <> 'PAID'"),
        "rosters": scalar("select count(*) from shift_rosters"),
        "attendance": scalar("select count(*) from attendance"),
        "pending_attendance_verification": scalar("select count(*) from attendance where verification_status not in ('VERIFIED','APPROVED')"),
        "employee_documents": scalar("select count(*) from employee_documents"),
        "expiring_documents_60d": scalar("select count(*) from employee_documents where expiry_date is not null and expiry_date between current_date and current_date + 60"),
        "expenses": scalar("select count(*) from expenses"),
        "corporate_compliances": scalar("select count(*) from corporate_compliances"),
        "overdue_compliances": scalar("select count(*) from corporate_compliances where due_date < current_date and status not in ('FILED','COMPLETED','COMPLIANT')"),
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


@router.get("/risk-engine")
def risk_engine(db: Session = Depends(get_db), current_user=Depends(require_owner)):
    """Read-only owner risk scan. It derives operational exceptions without mutating source records."""
    risks = []
    def add(code, category, severity, entity_type, entity_id, description):
        risks.append({"trigger_code": code, "category": category, "severity": severity, "entity_type": entity_type, "entity_id": str(entity_id) if entity_id is not None else None, "description": description})
    for r in db.execute(text("""select d.id,d.employee_id,e.employee_code,e.name,d.document_type,d.expiry_date from employee_documents d join employees e on e.id=d.employee_id where d.expiry_date < current_date order by d.expiry_date""")).mappings():
        add("DOC_EXPIRED","COMPLIANCE","HIGH","EMPLOYEE_DOCUMENT",r["id"],f'{r["document_type"]} expired for {r["employee_code"]} - {r["name"]}')
    for r in db.execute(text("""select id,invoice_number,client_id,due_date,total_amount from invoices where clearance_status <> 'PAID' and due_date < current_date order by due_date""")).mappings():
        add("INVOICE_OVERDUE","FINANCE","HIGH","INVOICE",r["id"],f'Invoice {r["invoice_number"]} is overdue')
    for r in db.execute(text("""select id,employee_id,month,amount from salary_records where lifecycle_status = 'HELD'""")).mappings():
        add("SALARY_HELD","PAYROLL","MEDIUM","SALARY_RECORD",r["id"],f'Salary for {r["month"]} is on hold')
    for r in db.execute(text("""select id,employee_id,exception_type,description from attendance_exceptions where resolved = false order by created_at desc""")).mappings():
        add("ATTENDANCE_EXCEPTION","OPERATIONS","MEDIUM","ATTENDANCE_EXCEPTION",r["id"],r["description"] or r["exception_type"])
    for r in db.execute(text("""select id,compliance_type,period,due_date from corporate_compliances where due_date < current_date and status not in ('FILED','COMPLETED','COMPLIANT') order by due_date""")).mappings():
        add("COMPLIANCE_OVERDUE","STATUTORY","HIGH","CORPORATE_COMPLIANCE",r["id"],f'{r["compliance_type"]} for {r["period"]} is overdue')
    return {"count": len(risks), "risks": risks}
