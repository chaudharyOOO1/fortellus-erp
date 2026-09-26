import { useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import api from '../api/axios';

export default function AccountSettings() {
  const [form,setForm]=useState({current_password:'',new_password:'',confirm:''});
  const [message,setMessage]=useState('');
  const [error,setError]=useState('');
  async function submit(e){
    e.preventDefault(); setMessage(''); setError('');
    if(form.new_password.length<12) return setError('New password must be at least 12 characters.');
    if(form.new_password!==form.confirm) return setError('New passwords do not match.');
    try { const r=await api.post('/auth/change-password',{current_password:form.current_password,new_password:form.new_password}); setMessage(r.data.message); setForm({current_password:'',new_password:'',confirm:''}); }
    catch(e){ setError(e.response?.data?.detail||'Unable to change password.'); }
  }
  return <MainLayout><div className="max-w-2xl space-y-5">
    <div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">My Account</p><h1 className="text-2xl font-bold text-slate-900 mt-1">Security & Password</h1><p className="text-sm text-slate-500 mt-1">Change your own ERP password at any time.</p></div>
    <form onSubmit={submit} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
      {message&&<div className="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-sm text-emerald-700">{message}</div>}
      {error&&<div className="rounded-lg bg-rose-50 border border-rose-200 px-3 py-2 text-sm text-rose-700">{error}</div>}
      {['current_password','new_password','confirm'].map((key)=><label key={key} className="block"><span className="text-xs font-semibold text-slate-600">{key==='current_password'?'Current password':key==='new_password'?'New password':'Confirm new password'}</span><input required type="password" value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-teal-500" /></label>)}
      <button className="rounded-lg bg-slate-900 text-white px-4 py-2.5 text-sm font-semibold hover:bg-slate-800">Change Password</button>
    </form>
  </div></MainLayout>
}