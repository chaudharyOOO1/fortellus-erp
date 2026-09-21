import { useEffect, useMemo, useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import api from '../api/axios';

const config = {
  payroll: { title:'Payroll & Salary', endpoint:'/erp/payroll', roles:'HR / Admin' },
  accounts: { title:'Accounts & GST', endpoint:'/erp/accounts', roles:'Accounts / Admin' },
  compliance: { title:'Compliance Control Center', endpoint:'/erp/compliance', roles:'HR / Admin' },
  risks: { title:'Risk & Controls', endpoint:'/erp/risks', roles:'Owner' },
};

function money(v) { return v == null ? '—' : Number(v).toLocaleString('en-IN', { maximumFractionDigits: 2 }); }

export default function Module({ type }) {
  const cfg = config[type] || config.payroll;
  const [data,setData]=useState(null), [error,setError]=useState('');
  useEffect(()=>{ setData(null); setError(''); api.get(cfg.endpoint).then(r=>setData(r.data)).catch(e=>setError(e.response?.data?.detail||'Unable to load module')); },[cfg.endpoint]);

  const sections = useMemo(()=>{
    if (!data) return [];
    if (type==='accounts') return [{title:'Invoices',rows:data.invoices||[]},{title:'Expenses',rows:data.expenses||[]},{title:'GST Collection',rows:data.gst_collection||[]},{title:'GST ITC',rows:data.gst_itc||[]}];
    if (type==='compliance') return [{title:'Employee Documents',rows:data.employee_documents||[]},{title:'Corporate Compliance',rows:data.corporate||[]}];
    return [{title:type==='risks'?'Open Risks':'Salary Records',rows:Array.isArray(data)?data:(data.salary_records||data.risks||[])}];
  },[data,type]);

  return <MainLayout><div className="space-y-5">
    <div><p className="text-[11px] font-mono tracking-[0.2em] text-cyan-400 uppercase">{cfg.roles}</p><h1 className="text-2xl font-black text-white">{cfg.title}</h1><p className="text-xs text-slate-400 mt-1">Live ERP records from the shared Supabase backend.</p></div>
    {error&&<div className="p-3 bg-red-500/10 text-red-300 rounded-xl text-xs">{error}</div>}
    {!data?<div className="cyber-panel rounded-2xl border border-slate-800 p-10 text-center text-slate-500">Loading...</div>:
      sections.map(s=><section key={s.title} className="cyber-panel rounded-2xl border border-slate-800 overflow-auto">
        <div className="px-4 py-3 border-b border-slate-800 flex justify-between"><span className="text-sm font-bold text-white">{s.title}</span><span className="text-xs text-slate-500">{s.rows.length} records</span></div>
        <table className="w-full text-left text-xs"><thead><tr className="bg-slate-900 text-slate-400"><th className="px-4 py-3">Record</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Date / Month</th><th className="px-4 py-3">Amount / Detail</th></tr></thead><tbody>
        {s.rows.length?s.rows.map((r,i)=><tr key={r.id||i} className="border-t border-slate-800/70"><td className="px-4 py-3 text-white">{r.name||r.company_name||r.employee_code||r.invoice_number||r.category||r.compliance_type||r.description||r.account_type||r.document_type||r.trigger_code||'Record'}</td><td className="px-4 py-3 text-cyan-300">{r.lifecycle_status||r.status||r.reconciliation_status||r.clearance_status||r.severity||'—'}</td><td className="px-4 py-3 text-slate-400">{r.month||r.due_date||r.expense_date||r.issue_date||r.entry_date||r.expiry_date||r.detected_at||'—'}</td><td className="px-4 py-3 text-slate-300">{r.net_pay!=null?money(r.net_pay):r.total_amount!=null?money(r.total_amount):r.amount!=null?money(r.amount):r.gst_amount!=null?money(r.gst_amount):r.description||r.reason||'—'}</td></tr>):<tr><td colSpan="4" className="p-8 text-center text-slate-500">No records found.</td></tr>}
        </tbody></table></section>)
    }
  </div></MainLayout>;
}