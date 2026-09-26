import { ShieldCheck } from 'lucide-react';

export default function OwnerExecutiveView() {
  return (
    <section className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-600">Owner clearance</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">Executive Command Center</h1>
        <p className="mt-2 text-sm text-slate-500">The production P&amp;L, balance sheet and risk radar will be activated in Phase 6.</p>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-teal-50 flex items-center justify-center text-teal-700"><ShieldCheck className="h-5 w-5" /></div>
          <div><h2 className="font-semibold text-slate-900">Owner-only workspace is protected</h2><p className="text-sm text-slate-500 mt-1">Only the OWNER role can open this route.</p></div>
        </div>
      </div>
    </section>
  );
}
