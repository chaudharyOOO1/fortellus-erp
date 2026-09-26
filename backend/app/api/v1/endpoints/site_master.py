from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_ops_or_admin
from app.core.database import get_db

router=APIRouter()

@router.get("")
def list_sites(db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    rows=db.execute(text("""select s.*,c.company_name,
      (select count(*) from site_rate_cards rc where rc.site_id=s.id and rc.is_active=true) as rate_card_count
      from sites s join clients c on c.id=s.client_id order by s.created_at desc""")).mappings().all()
    return [dict(r) for r in rows]

@router.get("/{site_id}")
def get_site(site_id:int,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    row=db.execute(text("select s.*,c.company_name from sites s join clients c on c.id=s.client_id where s.id=:id"),{"id":site_id}).mappings().first()
    if not row: raise HTTPException(404,"Site not found")
    return dict(row)

@router.post("",status_code=201)
def create_site(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    required=["client_id","site_name","address"]
    missing=[k for k in required if not payload.get(k)]
    if missing: raise HTTPException(422,f"Missing required fields: {', '.join(missing)}")
    if payload.get("latitude") is not None and not -90<=float(payload["latitude"])<=90: raise HTTPException(422,"Invalid latitude")
    if payload.get("longitude") is not None and not -180<=float(payload["longitude"])<=180: raise HTTPException(422,"Invalid longitude")
    allowed=["client_id","site_name","site_code","address","city","state","postal_code","branch","shift_requirements","contractual_rate","contact_phone","is_active","latitude","longitude","geofence_radius_meters"]
    data={k:payload[k] for k in allowed if k in payload}
    data.setdefault("shift_requirements",{}); data.setdefault("contractual_rate",0); data.setdefault("geofence_radius_meters",100); data.setdefault("is_active",True)
    cols=", ".join(data); binds=", ".join(f":{k}" for k in data)
    try:
        row=db.execute(text(f"insert into sites({cols}) values({binds}) returning *"),data).mappings().one()
        db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])

@router.patch("/{site_id}")
def update_site(site_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
    allowed={"client_id","site_name","site_code","address","city","state","postal_code","branch","shift_requirements","contractual_rate","contact_phone","is_active","latitude","longitude","geofence_radius_meters"}
    data={k:v for k,v in payload.items() if k in allowed}
    if not data: raise HTTPException(422,"No editable fields supplied")
    if "latitude" in data and data["latitude"] is not None and not -90<=float(data["latitude"])<=90: raise HTTPException(422,"Invalid latitude")
    if "longitude" in data and data["longitude"] is not None and not -180<=float(data["longitude"])<=180: raise HTTPException(422,"Invalid longitude")
    data["id"]=site_id; sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
    try:
        row=db.execute(text(f"update sites set {sets},updated_at=now() where id=:id returning *"),data).mappings().first()
        if not row: raise HTTPException(404,"Site not found")
        db.commit(); return dict(row)
    except HTTPException:
        db.rollback(); raise
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])
