from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_ops_or_admin
from app.core.database import get_db
router=APIRouter()
@router.get("")
def list_rosters(db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
 q="""select r.*,s.site_name,s.site_code,e.id employee_id,e.employee_code,e.name
 from shift_rosters r join sites s on s.id=r.site_id
 join guard_profiles g on g.id=r.guard_id left join employees e on e.id=g.employee_id
 order by r.date desc,r.created_at desc"""
 return [dict(r) for r in db.execute(text(q)).mappings().all()]
@router.get("/employees")
def roster_employees(db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
 q="""select g.id guard_id,g.employee_id,g.badge_number,e.employee_code,e.name,e.status from guard_profiles g join employees e on e.id=g.employee_id where g.status='ACTIVE' order by e.name"""
 return [dict(r) for r in db.execute(text(q)).mappings().all()]
@router.post("",status_code=201)
def create_roster(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
 for k in ("site_id","guard_id","date","shift_type"):
  if not payload.get(k): raise HTTPException(422,f"Missing required field: {k}")
 allowed=["site_id","guard_id","date","shift_type","status","notes"];data={k:payload[k] for k in allowed if k in payload};data.setdefault("status","SCHEDULED")
 try:
  row=db.execute(text("""insert into shift_rosters (site_id,guard_id,date,shift_type,status,notes) values (:site_id,:guard_id,:date,:shift_type,:status,:notes) returning *"""),data).mappings().one();db.commit();return dict(row)
 except Exception as exc:
  db.rollback();raise HTTPException(409,str(exc).split("\n")[0])
@router.patch("/{roster_id}")
def update_roster(roster_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
 allowed={"site_id","guard_id","date","shift_type","status","notes"};data={k:v for k,v in payload.items() if k in allowed}
 if not data:raise HTTPException(422,"No editable fields supplied")
 data["id"]=roster_id;sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
 row=db.execute(text(f"update shift_rosters set {sets} where id=:id returning *"),data).mappings().first()
 if not row:db.rollback();raise HTTPException(404,"Roster not found")
 db.commit();return dict(row)
