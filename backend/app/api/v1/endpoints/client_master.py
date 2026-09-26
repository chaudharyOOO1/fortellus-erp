from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_admin, get_current_active_user
from app.core.database import get_db

router = APIRouter()
READ_ROLES = {"OWNER", "SUPER_ADMIN", "ADMIN", "STAFF"}

def _assert_read_access(current_user):
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role not in READ_ROLES and not current_user.is_superuser:
        raise HTTPException(403, "You do not have permission to view client records.")

@router.get("")
def list_clients(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    _assert_read_access(current_user)
    rows = db.execute(text("""select c.*, coalesce(string_agg(e.name, ', ' order by e.name) filter (where cfo.is_active = true), '') as field_officers
        from clients c left join client_field_officers cfo on cfo.client_id = c.id left join employees e on e.id = cfo.employee_id
        group by c.id order by c.created_at desc""")).mappings().all()
    return [dict(r) for r in rows]

@router.get("/{client_id}")
def get_client(client_id:int, db:Session=Depends(get_db), current_user=Depends(get_current_active_user)):
    _assert_read_access(current_user)
    row=db.execute(text("""select c.*, coalesce(string_agg(e.name, ', ' order by e.name) filter (where cfo.is_active = true), '') as field_officers
        from clients c left join client_field_officers cfo on cfo.client_id = c.id left join employees e on e.id = cfo.employee_id
        where c.id=:id group by c.id"""),{"id":client_id}).mappings().first()
    if not row: raise HTTPException(404,"Client not found")
    return dict(row)

@router.get("/{client_id}/field-officers")
def get_client_field_officers(client_id:int, db:Session=Depends(get_db), current_user=Depends(get_current_active_user)):
    _assert_read_access(current_user)
    rows=db.execute(text("""select e.id,e.employee_code,e.name,e.designation,e.category,e.phone,cfo.assigned_at
        from client_field_officers cfo join employees e on e.id=cfo.employee_id
        where cfo.client_id=:client_id and cfo.is_active=true order by e.name"""),{"client_id":client_id}).mappings().all()
    return [dict(r) for r in rows]

@router.post("", status_code=201)
def create_client(payload:dict, db:Session=Depends(get_db), current_user=Depends(require_admin)):
    if not payload.get("company_name"): raise HTTPException(422,"Missing required fields: company_name")
    allowed=["client_code","company_name","registration_no","gst_number","billing_address","branch","gst_region","billing_cycle","contact_person","contact_email","contact_phone","credit_terms_days","is_active"]
    data={k:payload[k] for k in allowed if k in payload}; data.setdefault("credit_terms_days",30); data.setdefault("is_active",True)
    officer_ids=payload.get("field_officer_ids") or []
    try:
        row=db.execute(text(f"insert into clients ({', '.join(data)}) values ({', '.join(f':{k}' for k in data)}) returning *"),data).mappings().one()
        client_id=row["id"]
        for employee_id in officer_ids:
            db.execute(text("""insert into client_field_officers (client_id,employee_id)
                select :client_id,id from employees where id=:employee_id and lower(coalesce(status,'active'))='active'
                and lower(coalesce(category,'')) not like '%guard%'
                on conflict (client_id,employee_id) do update set is_active=true"""),{"client_id":client_id,"employee_id":employee_id})
        db.commit()
        result=dict(row)
        result["field_officers"]=", ".join(db.execute(text("""select e.name from client_field_officers cfo join employees e on e.id=cfo.employee_id
            where cfo.client_id=:client_id and cfo.is_active=true order by e.name"""),{"client_id":client_id}).scalars().all())
        return result
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])

@router.patch("/{client_id}")
def update_client(client_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    allowed={"client_code","company_name","registration_no","gst_number","billing_address","branch","gst_region","billing_cycle","contact_person","contact_email","contact_phone","credit_terms_days","is_active"}
    data={k:v for k,v in payload.items() if k in allowed}; officer_ids=payload.get("field_officer_ids",None)
    try:
        if data:
            data["id"]=client_id
            sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
            row=db.execute(text(f"update clients set {sets} where id=:id returning *"),data).mappings().first()
            if not row: raise HTTPException(404,"Client not found")
        else:
            row=db.execute(text("select * from clients where id=:id"),{"id":client_id}).mappings().first()
            if not row: raise HTTPException(404,"Client not found")
        if officer_ids is not None:
            db.execute(text("update client_field_officers set is_active=false where client_id=:client_id"),{"client_id":client_id})
            for employee_id in officer_ids:
                db.execute(text("insert into client_field_officers (client_id,employee_id) values (:client_id,:employee_id) on conflict (client_id,employee_id) do update set is_active=true"),{"client_id":client_id,"employee_id":employee_id})
        db.commit(); return dict(row)
    except HTTPException:
        db.rollback(); raise
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])
