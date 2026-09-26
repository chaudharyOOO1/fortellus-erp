from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_admin, get_current_active_user
from app.core.database import get_db

router=APIRouter()

@router.get("")
def list_contracts(db:Session=Depends(get_db), current_user=Depends(get_current_active_user)):
    rows=db.execute(text("""
      select cc.*, c.company_name,
        case
          when cc.contract_end_date < current_date then 'EXPIRED'
          when cc.contract_end_date <= current_date + interval '30 days' then 'EXPIRING_30'
          when cc.contract_end_date <= current_date + interval '60 days' then 'EXPIRING_60'
          else 'NORMAL'
        end as renewal_status
      from client_contracts cc join clients c on c.id=cc.client_id
      order by cc.contract_end_date asc
    """)).mappings().all()
    return [dict(r) for r in rows]

@router.post("",status_code=201)
def create_contract(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    required=["client_id","contract_number","contract_start_date","contract_end_date"]
    missing=[k for k in required if not payload.get(k)]
    if missing: raise HTTPException(422,f"Missing required fields: {', '.join(missing)}")
    allowed=["client_id","contract_number","contract_start_date","contract_end_date","billing_cycle","credit_terms_days","wage_indexation_percent","status","renewal_notes"]
    data={k:payload[k] for k in allowed if k in payload}
    data.setdefault("billing_cycle","MONTHLY"); data.setdefault("credit_terms_days",30); data.setdefault("wage_indexation_percent",0); data.setdefault("status","ACTIVE")
    try:
        row=db.execute(text("""insert into client_contracts
          (client_id,contract_number,contract_start_date,contract_end_date,billing_cycle,credit_terms_days,wage_indexation_percent,status,renewal_notes)
          values (:client_id,:contract_number,:contract_start_date,:contract_end_date,:billing_cycle,:credit_terms_days,:wage_indexation_percent,:status,:renewal_notes)
          returning *"""),data).mappings().one()
        db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])

@router.patch("/{contract_id}")
def update_contract(contract_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    allowed={"contract_number","contract_start_date","contract_end_date","billing_cycle","credit_terms_days","wage_indexation_percent","status","renewal_notes"}
    data={k:v for k,v in payload.items() if k in allowed}
    if not data: raise HTTPException(422,"No editable fields supplied")
    data["id"]=contract_id
    sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
    try:
        row=db.execute(text(f"update client_contracts set {sets},updated_at=now() where id=:id returning *"),data).mappings().first()
        if not row: raise HTTPException(404,"Contract not found")
        db.commit(); return dict(row)
    except HTTPException:
        db.rollback(); raise
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])

@router.get("/site/{site_id}/rates")
def list_site_rates(site_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_active_user)):
    rows=db.execute(text("select * from site_rate_cards where site_id=:site_id order by vertical,category,effective_from desc"),{"site_id":site_id}).mappings().all()
    return [dict(r) for r in rows]

@router.post("/site/{site_id}/rates",status_code=201)
def create_site_rate(site_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    required=["vertical","category"]
    missing=[k for k in required if not payload.get(k)]
    if missing: raise HTTPException(422,f"Missing required fields: {', '.join(missing)}")
    if payload["vertical"] not in {"SECURITY","HOUSEKEEPING","NURSING"}: raise HTTPException(422,"Invalid vertical")
    data={k:payload[k] for k in ["vertical","category","hourly_rate","daily_rate","wage_indexation_percent","effective_from","effective_to","is_active"] if k in payload}
    data["site_id"]=site_id; data.setdefault("hourly_rate",0); data.setdefault("daily_rate",0); data.setdefault("wage_indexation_percent",0); data.setdefault("is_active",True)
    try:
        row=db.execute(text("""insert into site_rate_cards
          (site_id,vertical,category,hourly_rate,daily_rate,wage_indexation_percent,effective_from,effective_to,is_active)
          values (:site_id,:vertical,:category,:hourly_rate,:daily_rate,:wage_indexation_percent,
                  coalesce(:effective_from,current_date),:effective_to,:is_active) returning *"""),data).mappings().one()
        db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])
