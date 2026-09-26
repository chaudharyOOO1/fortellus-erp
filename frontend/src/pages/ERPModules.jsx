import { useEffect, useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import GlassCard from '../components/GlassCard';
import StatCard from '../components/StatCard';
import api from '../api/axios';
import {
  Users, Building2, MapPin, WalletCards, FileWarning, ReceiptText,
  ShieldCheck, UserPlus, BriefcaseBusiness, ClipboardCheck, IndianRupee
} from 'lucide-react';

const modules = [
  { title: 'Employees', subtitle: 'Employee master, documents, bank, nominee & uniforms', path: '/employees', icon: Users },
  { title: 'Clients', subtitle: 'Clients, contracts, contacts and billing configuration', path: '/clients', icon: Building2 },
  { title: 'Sites', subtitle: 'Deployment locations and manpower requirements', path: '/sites', icon: MapPin },
  { title: 'Operations', subtitle: 'Rosters, deployment and attendance control', path: '/rosters', icon: ClipboardCheck },
  { title: 'Payroll', subtitle: 'Salary records, holds and payroll processing', path: '/payroll', icon: WalletCards },
  { title: 'Accounts & GST', subtitle: 'Invoices, expenses, GST and bookkeeping', path: '/accounts', icon: ReceiptText },
  { title: 'Compliance', subtitle: 'Documents, expiry tracking and statutory controls', path: '/compliance', icon: ShieldCheck },
  { title: 'Risk & Controls', subtitle: 'Owner-level risks and exception monitoring', path: '/risks', icon: FileWarning },
];

export default function ERPModules() {
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/erp/summary')
      .then(({ data }) => setSummary(data || {}))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const stats = [
    ['Employees', summary.employees ?? 0, Users],
    ['Clients', summary.clients ?? 0, Building2],
    ['Active Sites', summary.active_sites ?? 0, MapPin],
    ['Salary Records', summary.salary_records ?? 0, IndianRupee],
    ['Unpaid Invoices', summary.unpaid_invoices ?? 0, ReceiptText],
    ['Open Risks', summary.open_risks ?? 0, FileWarning],
    ['Rosters', summary.rosters ?? 0, ClipboardCheck],
    ['Attendance', summary.attendance ?? 0, ClipboardCheck],
    ['Docs Expiring ≤60d', summary.expiring_documents_60d ?? 0, FileWarning],
    ['Overdue Compliance', summary.overdue_compliances ?? 0, ShieldCheck],
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <section className="bg-white border border-slate-200 rounded-2xl p-5 sm:p-6 shadow-sm">
          <p className="text-[11px] font-semibold tracking-[0.18em] text-teal-700 uppercase">Northlane Allied Services • Enterprise Resource Planning</p>
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-3 mt-2">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">ERP Command Center</h1>
              <p className="text-sm text-slate-500 mt-1.5 max-w-3xl">
                One administrative system for clients, employees, deployments, attendance, payroll, accounts, compliance and risk.
              </p>
            </div>
            <div className="text-xs text-slate-400">Northlane Allied Services</div>
          </div>
        </section>

        <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {stats.map(([label, value, Icon]) => (
            <StatCard key={label} label={label} value={loading ? '—' : value} icon={Icon} />
          ))}
        </section>

        <GlassCard glow>
          <GlassCard.Header
            title="ERP Modules"
            subtitle="Select a module to manage operational data"
            badge
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {modules.map(({ title, subtitle, path, icon: Icon }) => (
              <button
                key={title}
                onClick={() => window.location.assign(path)}
                className="text-left p-5 rounded-xl border border-slate-200 bg-white hover:border-teal-200 hover:shadow-md transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 group-hover:scale-105 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-sm font-semibold text-slate-900 mt-4">{title}</h3>
                <p className="text-xs text-slate-500 mt-1 leading-5">{subtitle}</p>
              </button>
            ))}
          </div>
        </GlassCard>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <GlassCard>
            <GlassCard.Header title="Current Architecture" subtitle="Single source of truth" />
            <div className="space-y-3 text-xs text-slate-600">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200"><b className="text-teal-700">ERP Web</b> → FastAPI → Supabase</div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200"><b className="text-emerald-700">Employee APK</b> → same backend → same employee records</div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200"><b className="text-amber-700">Owner Controls</b> → finance, GST, risk and audit visibility</div>
            </div>
          </GlassCard>

          <GlassCard>
            <GlassCard.Header title="Quick Actions" subtitle="Common administrative tasks" />
            <div className="grid grid-cols-2 gap-2">
              <button onClick={() => window.location.assign('/employees')} className="p-3 rounded-lg border border-slate-200 hover:border-teal-200 hover:bg-teal-50 text-xs font-semibold text-slate-700 text-left"><UserPlus className="w-4 h-4 text-teal-700 mb-1" />Add Employee</button>
              <button onClick={() => window.location.assign('/clients')} className="p-3 rounded-lg border border-slate-200 hover:border-teal-200 hover:bg-teal-50 text-xs font-semibold text-slate-700 text-left"><BriefcaseBusiness className="w-4 h-4 text-purple-600 mb-1" />Add Client</button>
            </div>
          </GlassCard>

          <GlassCard>
            <GlassCard.Header title="Data Status" subtitle="Backend connection" />
            <div className="p-4 rounded-xl border border-emerald-100 bg-emerald-50">
              <div className="flex items-center gap-2 text-emerald-700 font-semibold text-sm"><ShieldCheck className="w-5 h-5" /> Live ERP data layer</div>
              <p className="text-xs text-slate-500 mt-2">Dashboard metrics are requested from the ERP API instead of hard-coded UI values.</p>
            </div>
          </GlassCard>
        </div>
      </div>
    </MainLayout>
  );
}
