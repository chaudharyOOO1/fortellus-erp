from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_hr_or_admin
from app.core.database import get_db

router=APIRouter()

def lock_reasons(row):
    today=date.today(); reasons=[]
    if row.get("police_verification_expiry") is None or row["police_verification_expiry"]<today: reasons.append("Police Verification expired or missing")
    if row.get("medical_fitness_expiry") is None or row["medical_fitness_expiry"]<today: reasons.append("Medical Fitness expired or missing")
    return reasons

@router.get("")
def list_staff(db:Session=Depends(get_db),current_user=Depends(require_hr_or_admin)):
    rows=db.execute(text("""select s.*,e.name,e.phone,e.employee_code,e.branch,e.joining_date from staff_profiles s join employees e on e.id=s.employee_id order by e.name""")).mappings().all()
    return [dict(r) for r in rows]

@router.post("/{employee_id}/compliance-check")
def compliance_check(employee_id:str,db:Session=Depends(get_db),current_user=Depends(require_hr_or_admin)):
    row=db.execute(text("select * from staff_profiles where employee_id=:id for update"),{"id":employee_id}).mappings().first()
    if not row: raise HTTPException(404,"Staff profile not found.")
    reasons=lock_reasons(row); locked=bool(reasons); status="BENCH" if locked else ("ACTIVE" if row["status"]=="BENCH" else row["status"]); reason="; ".join(reasons) if reasons else None
    db.execute(text("update staff_profiles set status=:status,is_bench_locked=:locked,bench_lock_reason=:reason,updated_at=now() where employee_id=:id"),{"status":status,"locked":locked,"reason":reason,"id":employee_id})
    db.execute(text("update employees set status=:status,status_reason=:reason where id=:id"),{"status":"bench" if locked else "active","reason":reason,"id":employee_id})
    db.commit(); return dict(db.execute(text("select * from staff_profiles where employee_id=:id"),{"id":employee_id}).mappings().one())

@router.post("/compliance/run")
def run_compliance(db:Session=Depends(get_db),current_user=Depends(require_hr_or_admin)):
    rows=db.execute(text("select * from staff_profiles")).mappings().all(); locked=0
    for row in rows:
        reasons=lock_reasons(row); is_locked=bool(reasons); status="BENCH" if is_locked else ("ACTIVE" if row["status"]=="BENCH" else row["status"]); reason="; ".join(reasons) if reasons else None
        db.execute(text("update staff_profiles set status=:status,is_bench_locked=:locked,bench_lock_reason=:reason,updated_at=now() where employee_id=:id"),{"status":status,"locked":is_locked,"reason":reason,"id":str(row["employee_id"])})
        db.execute(text("update employees set status=:status,status_reason=:reason where id=:id"),{"status":"bench" if is_locked else "active","reason":reason,"id":str(row["employee_id"])}); locked+=int(is_locked)
    db.commit(); return {"checked":len(rows),"bench_locked":locked}

@router.patch("/{employee_id}")
def update_staff(employee_id:str,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_hr_or_admin)):
    allowed={"vertical","category","aadhaar_number","pan_number","bank_account_no","bank_name","bank_ifsc","nominee_name","nominee_relation","nominee_aadhaar","arms_license_no","arms_expiry_date","arms_caliber","ammunition_count","uniform_total_cost","uniform_monthly_emi","uniform_balance_due","police_verification_expiry","medical_fitness_expiry","psara_cert_no","psara_training_expiry","gun_license_expiry","badge_number"}
    data={k:v for k,v in payload.items() if k in allowed}
    if "aadhaar_number" in data and data["aadhaar_number"] and not __import__("app.api.v1.endpoints.recruitment",fromlist=["verhoeff"]).verhoeff(data["aadhaar_number"]): raise HTTPException(422,"Aadhaar failed 12-digit Verhoeff checksum validation.")
    if not data: raise HTTPException(422,"No editable staff fields supplied.")
    data["employee_id"]=employee_id; sets=", ".join(f"{k}=:{k}" for k in data if k!="employee_id")
    row=db.execute(text(f"update staff_profiles set {sets},updated_at=now() where employee_id=:employee_id returning *"),data).mappings().first()
    if not row: raise HTTPException(404,"Staff profile not found.")
    db.commit(); return dict(row)
