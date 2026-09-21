from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_ops_or_admin
from app.core.database import get_db
router=APIRouter()
@router.get("")
def list_attendance(db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
 q="""select a.*,e.employee_code,e.name,s.site_name from attendance a join employees e on e.id=a.employee_id left join shift_rosters r on r.id=a.roster_id left join sites s on s.id=r.site_id order by a.attendance_date desc,a.created_at desc"""
 return [dict(r) for r in db.execute(text(q)).mappings().all()]
@router.patch("/{attendance_id}")
def update_attendance(attendance_id:str,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_ops_or_admin)):
 allowed={"status","shift_hours","overtime_hours","late_minutes","violation_type","client_verified","verification_status","verified_at"};data={k:v for k,v in payload.items() if k in allowed}
 if not data:raise HTTPException(422,"No editable fields supplied")
 data["id"]=attendance_id;sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
 row=db.execute(text(f"update attendance set {sets} where id=cast(:id as uuid) returning *"),data).mappings().first()
 if not row:db.rollback();raise HTTPException(404,"Attendance not found")
 db.commit();return dict(row)
