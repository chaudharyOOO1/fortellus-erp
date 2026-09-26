import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_admin, get_current_active_user
from app.core.database import get_db

router=APIRouter()
READ_ROLES={"OWNER","SUPER_ADMIN","ADMIN","HR","OPERATIONS","ACCOUNTS","SUPERVISOR","CLIENT"}
GSTIN_RE=re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")

def _role(user):
    return user.role.value if hasattr(user.role,"value") else str(user.role)

def _assert_read_access(user):
    if _role(user) not in READ_ROLES and not user.is_superuser:
        raise HTTPException(403,"You do not have permission to view client records.")

def _validate_gstin(payload):
    gstin=(payload.get("gstin") or payload.get("gst_number") or "").strip().upper()
    if not gstin or not GSTIN_RE.fullmatch(gstin):
        raise HTTPException(422,"GSTIN must be a valid 15-character GSTIN.")
    return gstin

@router.get("")
def list_clients(db:Session=Depends(get_db),current_user=Depends(get_current_active_user)):
    _assert_read_access(current_user)
    rows=db.execute(text("""
      select c.*,
        coalesce(string_agg(e.name, ', ' order by e.name) filter (where cfo.is_active=true),'') as field_officers,
        count(distinct s.id) as site_count,
        count(distinct cc.id) filter (where cc.status='ACTIVE') as active_contract_count,
        min(cc.contract_end_date) filter (where cc.status in ('ACTIVE','RENEWED')) as nearest_contract_end,
        case
          when min(cc.contract_end_date) filter (where cc.status in ('ACTIVE','RENEWED')) < current_date then 'EXPIRED'
          when min(cc.contract_end_date) filter (where cc.status in ('ACTIVE','RENEWED')) <= current_date + interval '30 days' then 'EXPIRING_30'
          when min(cc.contract_end_date) filter (where cc.status in ('ACTIVE','RENEWED')) <= current_date + interval '60 days' then 'EXPIRING_60'
          else 'NORMAL'
        end as renewal_status
      from clients c
      left join client_field_officers cfo on cfo.client_id=c.id
      left join employees e on e.id=cfo.employee_id
      left join sites s on s.client_id=c.id and s.is_active=true
      left join client_contracts cc on cc.client_id=c.id
      group by c.id order by c.created_at desc
    """)).mappings().all()
    return [dict(r) for r in rows]

@router.get("/{client_id}")
def get_client(client_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_active_user)):
    _assert_read_access(current_user)
    row=db.execute(text("""
      select c.*,
        coalesce(string_agg(distinct e.name, ', ' order by e.name) filter (where cfo.is_active=true),'') as field_officers,
        count(distinct s.id) filter (where s.is_active=true) as site_count,
        min(cc.contract_end_date) filter (where cc.status in ('ACTIVE','RENEWED')) as nearest_contract_end
      from clients c
      left join client_field_officers cfo on cfo.client_id=c.id
      left join employees e on e.id=cfo.employee_id
      left join sites s on s.client_id=c.id
      left join client_contracts cc on cc.client_id=c.id
      where c.id=:id group by c.id
    """),{"id":client_id}).mappings().first()
    if not row: raise HTTPException(404,"Client not found")
    return dict(row)

@router.get("/{client_id}/field-officers")
def get_client_field_officers(client_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_active_user)):
    _assert_read_access(current_user)
    rows=db.execute(text("""select e.id,e.employee_code,e.name,e.designation,e.category,e.phone,cfo.assigned_at
      from client_field_officers cfo join employees e on e.id=cfo.employee_id
      where cfo.client_id=:client_id and cfo.is_active=true order by e.name"""),{"client_id":client_id}).mappings().all()
    return [dict(r) for r in rows]

@router.post("",status_code=201)
def create_client(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    if not payload.get("company_name"): raise HTTPException(422,"Missing required fields: company_name")
    gstin=_validate_gstin(payload)
    region=payload.get("branch_region")
    if region and region not in {"UTTARAKHAND","UTTAR_PRADESH","DELHI_NCR"}:
        raise HTTPException(422,"branch_region must be UTTARAKHAND, UTTAR_PRADESH or DELHI_NCR")
    allowed=["client_code","company_name","registration_no","gst_number","gstin","billing_address","branch","gst_region","branch_region","billing_cycle","contact_person","contact_email","contact_phone","credit_terms_days","contract_start_date","contract_end_date","is_active"]
    data={k:payload[k] for k in allowed if k in payload}
    data["gstin"]=gstin; data["gst_number"]=gstin
    data.setdefault("credit_terms_days",30); data.setdefault("is_active",True)
    officer_ids=payload.get("field_officer_ids") or []
    try:
        row=db.execute(text(f"insert into clients ({', '.join(data)}) values ({', '.join(':'+k for k in data)}) returning *"),data).mappings().one()
        client_id=row["id"]
        for employee_id in officer_ids:
            db.execute(text("""insert into client_field_officers(client_id,employee_id)
              select :client_id,id from employees where id=:employee_id and lower(coalesce(status,'active'))='active'
              and lower(coalesce(category,'')) not like '%guard%'
              on conflict(client_id,employee_id) do update set is_active=true"""),{"client_id":client_id,"employee_id":employee_id})
        db.commit()
        return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])

@router.patch("/{client_id}")
def update_client(client_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    data={k:v for k,v in payload.items() if k in {"client_code","company_name","registration_no","gst_number","gstin","billing_address","branch","gst_region","branch_region","billing_cycle","contact_person","contact_email","contact_phone","credit_terms_days","contract_start_date","contract_end_date","is_active"}}
    if "gstin" in data or "gst_number" in data:
        data["gstin"]=_validate_gstin(payload); data["gst_number"]=data["gstin"]
    officer_ids=payload.get("field_officer_ids")
    if not data and officer_ids is None: raise HTTPException(422,"No editable fields supplied")
    try:
        if data:
            data["id"]=client_id
            sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
            row=db.execute(text(f"update clients set {sets},updated_at=now() where id=:id returning *"),data).mappings().first()
            if not row: raise HTTPException(404,"Client not found")
        else:
            row=db.execute(text("select * from clients where id=:id"),{"id":client_id}).mappings().first()
            if not row: raise HTTPException(404,"Client not found")
        if officer_ids is not None:
            db.execute(text("update client_field_officers set is_active=false where client_id=:client_id"),{"client_id":client_id})
            for employee_id in officer_ids:
                db.execute(text("insert into client_field_officers(client_id,employee_id) values(:client_id,:employee_id) on conflict(client_id,employee_id) do update set is_active=true"),{"client_id":client_id,"employee_id":employee_id})
        db.commit(); return dict(row)
    except HTTPException:
        db.rollback(); raise
    except Exception as exc:
        db.rollback(); raise HTTPException(409,str(exc).split("\n")[0])
