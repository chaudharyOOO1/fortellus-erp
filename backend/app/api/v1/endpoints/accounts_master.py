from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import require_accounts_or_admin
from app.core.database import get_db

router=APIRouter()

@router.post("/accounts/invoices")
def create_invoice(payload: dict, db: Session=Depends(get_db), current_user=Depends(require_accounts_or_admin)):
    required=["client_id","invoice_number","billing_month","due_date","subtotal"]
    if any(payload.get(k) in (None,"") for k in required): raise HTTPException(400,"client_id, invoice_number, billing_month, due_date and subtotal are required")
    subtotal=float(payload["subtotal"]); rate=float(payload.get("tax_rate",18)); mode=str(payload.get("tax_mode","INTRA")).upper()
    tax=round(subtotal*rate/100,2); cgst=round(tax/2,2) if mode=="INTRA" else 0; sgst=round(tax/2,2) if mode=="INTRA" else 0; igst=tax if mode=="INTER" else 0
    data={"client_id":payload["client_id"],"invoice_number":payload["invoice_number"],"billing_month":payload["billing_month"],"due_date":payload["due_date"],"subtotal":subtotal,"tax_rate":rate,"cgst":cgst,"sgst":sgst,"igst":igst,"tax_amount":tax,"total_amount":subtotal+tax,"status":payload.get("status","DRAFT"),"clearance_status":payload.get("clearance_status","PENDING"),"notes":payload.get("notes")}
    cols=", ".join(data); vals=", ".join(f":{k}" for k in data)
    row=db.execute(text(f"insert into invoices ({cols}) values ({vals}) returning *"),data).mappings().one()
    return dict(row)

@router.patch("/accounts/invoices/{invoice_id}")
def update_invoice(invoice_id:int,payload:dict,db:Session=Depends(get_db),current_user=Depends(require_accounts_or_admin)):
    allowed=["status","clearance_status","due_date","notes","billing_month"]
    data={k:v for k,v in payload.items() if k in allowed}; data["id"]=invoice_id
    if len(data)==1: raise HTTPException(400,"No editable fields supplied")
    sets=", ".join(f"{k}=:{k}" for k in data if k!="id")
    row=db.execute(text(f"update invoices set {sets},updated_at=now() where id=:id returning *"),data).mappings().first()
    if not row: raise HTTPException(404,"Invoice not found")
    return dict(row)

@router.post("/accounts/expenses")
def create_expense(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_accounts_or_admin)):
    if not payload.get("category") or payload.get("amount") is None: raise HTTPException(400,"category and amount are required")
    data={k:payload.get(k) for k in ["branch","client_id","category","description","amount","expense_date"] if payload.get(k) is not None}
    cols=", ".join(data); vals=", ".join(f":{k}" for k in data)
    row=db.execute(text(f"insert into expenses ({cols}) values ({vals}) returning *"),data).mappings().one()
    return dict(row)

@router.post("/accounts/bookkeeping")
def create_bookkeeping_entry(payload:dict,db:Session=Depends(get_db),current_user=Depends(require_accounts_or_admin)):
    if not payload.get("account_type"): raise HTTPException(400,"account_type is required")
    data={k:payload.get(k) for k in ["entry_date","account_type","reference_type","reference_id","debit","credit","description"] if payload.get(k) is not None}
    cols=", ".join(data); vals=", ".join(f":{k}" for k in data)
    row=db.execute(text(f"insert into bookkeeping_ledger ({cols}) values ({vals}) returning *"),data).mappings().one()
    return dict(row)
