from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_admin, require_accounts_or_admin
from app.core.database import get_db

router = APIRouter()

@router.get("")
def list_clients(db: Session=Depends(get_db), current_user=Depends(require_admin)):
    return [dict(r) for r in db.execute(text("select * from clients order by created_at desc")).mappings().all()]

@router.post("", status_code=201)
def create_client(payload: dict, db: Session=Depends(get_db), current_user=Depends(require_admin)):
    required=["company_name"]
    missing=[k for k in required if not payload.get(k)]
    if missing: raise HTTPException(422, f"Missing required fields: {', '.join(missing)}")
    allowed=["client_code","company_name","registration_no","gst_number","billing_address","branch","gst_region","billing_cycle","contact_person","contact_email","contact_phone","credit_terms_days","is_active"]
    data={k:payload[k] for k in allowed if k in payload}
    data.setdefault("credit_terms_days",30); data.setdefault("is_active",True)
    cols=", ".join(data); binds=", ".join(f":{k}" for k in data)
    try:
        row=db.execute(text(f"insert into clients ({cols}) values ({binds}) returning *"),data).mappings().one(); db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])

@router.patch("/{client_id}")
def update_client(client_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    allowed={"client_code","company_name","registration_no","gst_number","billing_address","branch","gst_region","billing_cycle","contact_person","contact_email","contact_phone","credit_terms_days","is_active"}
    data={k:v for k,v in payload.items() if k in allowed}
    if not data: raise HTTPException(422,"No editable fields supplied")
    data["id"]=client_id
    sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
    row=db.execute(text(f"update clients set {sets} where id=:id returning *"),data).mappings().first()
    if not row: db.rollback(); raise HTTPException(404,"Client not found")
    db.commit(); return dict(row)
