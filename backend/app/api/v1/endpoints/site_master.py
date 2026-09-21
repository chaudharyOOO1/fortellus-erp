from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_ops_or_admin
from app.core.database import get_db
router=APIRouter()
@router.get("")
def list_sites(db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    q="""select s.*, c.company_name from sites s join clients c on c.id=s.client_id order by s.created_at desc"""
    return [dict(r) for r in db.execute(text(q)).mappings().all()]
@router.post("",status_code=201)
def create_site(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    required=["client_id","site_name","address"]
    missing=[k for k in required if not payload.get(k)]
    if missing: raise HTTPException(422,f"Missing required fields: {', '.join(missing)}")
    allowed=["client_id","site_name","site_code","address","city","state","postal_code","branch","shift_requirements","contractual_rate","contact_phone","is_active"]
    data={k:payload[k] for k in allowed if k in payload}; data.setdefault("shift_requirements",{}); data.setdefault("contractual_rate",0); data.setdefault("is_active",True)
    cols=", ".join(data); binds=", ".join(f":{k}" for k in data)
    try:
        row=db.execute(text(f"insert into sites ({cols}) values ({binds}) returning *"),data).mappings().one(); db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])
@router.patch("/{site_id}")
def update_site(site_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    allowed={"client_id","site_name","site_code","address","city","state","postal_code","branch","shift_requirements","contractual_rate","contact_phone","is_active"}
    data={k:v for k,v in payload.items() if k in allowed}
    if not data: raise HTTPException(422,"No editable fields supplied")
    data["id"]=site_id; sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
    row=db.execute(text(f"update sites set {sets} where id=:id returning *"),data).mappings().first()
    if not row: db.rollback(); raise HTTPException(404,"Site not found")
    db.commit(); return dict(row)
