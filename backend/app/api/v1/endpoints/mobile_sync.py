from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db

router=APIRouter()

@router.get("/mobile/me")
def mobile_me(db:Session=Depends(get_db), current_user=Depends(get_current_active_user)):
    q="""select e.id employee_id,e.employee_code,e.name,e.phone,e.status,e.designation,e.branch,e.site_id,
                 g.id guard_profile_id,g.badge_number,g.daily_rate,g.status guard_status,
                 s.site_name,s.address site_address
          from users u
          left join guard_profiles g on g.user_id=u.id
          left join employees e on e.id=g.employee_id
          left join sites s on s.id=e.site_id
          where u.id=:uid"""
    row=db.execute(text(q),{"uid":current_user.id}).mappings().first()
    if not row or not row["employee_id"]:
        raise HTTPException(404,"No employee profile is linked to this login")
    return dict(row)

@router.get("/mobile/me/attendance")
def mobile_attendance(db:Session=Depends(get_db), current_user=Depends(get_current_active_user)):
    q="""select a.*,r.shift_type,r.date roster_date,s.site_name
         from attendance a
         left join shift_rosters r on r.id=a.roster_id
         left join sites s on s.id=r.site_id
         join guard_profiles g on g.employee_id=a.employee_id
         where g.user_id=:uid
         order by a.attendance_date desc limit 60"""
    return [dict(r) for r in db.execute(text(q),{"uid":current_user.id}).mappings().all()]

@router.get("/mobile/me/salary")
def mobile_salary(db:Session=Depends(get_db), current_user=Depends(get_current_active_user)):
    q="""select s.* from salary_records s
         join guard_profiles g on g.employee_id=s.employee_id
         where g.user_id=:uid order by s.month desc limit 24"""
    return [dict(r) for r in db.execute(text(q),{"uid":current_user.id}).mappings().all()]
