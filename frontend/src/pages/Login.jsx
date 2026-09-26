import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { Eye, EyeOff, LockKeyhole, Mail, Loader2, ShieldCheck, ArrowRight, KeyRound } from 'lucide-react';
import { INITIAL_USERS } from '../api/mockData';

export default function Login() {
  const [email, setEmail] = useState('owner@fortellus.com');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, loading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  async function handlePersonaLogin(persona) {
    setError('');
    setEmail(persona.email);
    setPassword(persona.personaPassword);
    const result = await login(persona.email, persona.personaPassword);
    if (result.success) navigate('/dashboard', { replace: true });
    else setError(result.error || 'Persona login failed.');
  }

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard', { replace: true });
  }, [isAuthenticated, navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const result = await login(email.trim(), password);
    if (result.success) navigate('/dashboard', { replace: true });
    else setError(result.error || 'Unable to sign in. Check your credentials.');
  }

  return (
    <main className="min-h-screen bg-white text-slate-900 flex">
      <section className="hidden lg:flex lg:w-[46%] bg-slate-950 text-white relative overflow-hidden p-12 xl:p-16 flex-col justify-between">
        <div className="absolute inset-0 opacity-20" style={{backgroundImage:'linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px)', backgroundSize:'48px 48px'}} />
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="h-11 w-11 rounded-xl bg-white flex items-center justify-center shadow-lg"><ShieldCheck className="h-6 w-6 text-slate-950" /></div>
            <div><div className="text-xl font-bold tracking-tight">FORTELLUS</div><div className="text-[10px] tracking-[.28em] text-slate-400">ENTERPRISE ERP</div></div>
          </div>
        </div>
        <div className="relative max-w-lg">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 mb-6"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Secure operations platform</div>
          <h1 className="text-4xl xl:text-5xl font-semibold tracking-tight leading-[1.08]">One control center for your workforce.</h1>
          <p className="mt-5 text-base leading-7 text-slate-400 max-w-md">Manage clients, sites, employees, attendance, payroll and billing from a single operational workspace.</p>
        </div>
        <div className="relative flex items-center gap-6 text-xs text-slate-500"><span>© {new Date().getFullYear()} Fortellus</span><span>•</span><span>Administrator access</span></div>
      </section>
      <section className="w-full lg:w-[54%] flex items-center justify-center px-5 py-10 sm:px-8">
        <div className="w-full max-w-[440px]">
          <div className="lg:hidden flex items-center gap-3 mb-12"><div className="h-10 w-10 rounded-xl bg-slate-950 flex items-center justify-center"><ShieldCheck className="h-5 w-5 text-white" /></div><div><div className="font-bold tracking-tight">FORTELLUS</div><div className="text-[9px] tracking-[.25em] text-slate-400">ENTERPRISE ERP</div></div></div>
          <div className="mb-9"><p className="text-xs font-semibold uppercase tracking-[.18em] text-slate-500">Fortellus enterprise portal</p><h2 className="mt-3 text-3xl font-semibold tracking-tight">Welcome back</h2><p className="mt-2 text-sm text-slate-500">Sign in to continue to your Fortellus workspace.</p></div>
          <div className="mb-7"><p className="mb-3 text-xs font-semibold uppercase tracking-[.16em] text-slate-400">Quick persona login</p><div className="grid grid-cols-2 sm:grid-cols-3 gap-2">{INITIAL_USERS.filter(u => ['OWNER','HR','OPERATIONS','ACCOUNTS','CLIENT','STAFF'].includes(u.role) && u.personaPassword).map((persona) => (<button key={persona.role} type="button" onClick={() => handlePersonaLogin(persona)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-left hover:border-slate-400 hover:bg-white transition-colors"><span className="block text-xs font-semibold text-slate-800">{persona.role === 'STAFF' ? 'Employee' : persona.role}</span><span className="block text-[10px] text-slate-400 mt-0.5 truncate">{persona.email}</span></button>))}</div></div>
          {error && <div role="alert" className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div><label htmlFor="email" className="mb-2 block text-sm font-medium text-slate-700">Email address</label><div className="relative"><Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input id="email" type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} className="h-12 w-full rounded-xl border border-slate-300 bg-white pl-10 pr-4 text-sm outline-none transition focus:border-slate-900 focus:ring-4 focus:ring-slate-900/5" placeholder="owner@fortellus.com" /></div></div>
            <div><label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-700">Password</label><div className="relative"><LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input id="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} className="h-12 w-full rounded-xl border border-slate-300 bg-white pl-10 pr-12 text-sm outline-none transition focus:border-slate-900 focus:ring-4 focus:ring-slate-900/5" placeholder="Enter your password" /><button type="button" onClick={() => setShowPassword(v => !v)} aria-label={showPassword ? 'Hide password' : 'Show password'} className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-700">{showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button></div></div>
            <button type="submit" disabled={loading} className="h-12 w-full rounded-xl bg-slate-950 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 flex items-center justify-center gap-2">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <>Sign in <ArrowRight className="h-4 w-4" /></>}</button>
          </form>
          <div className="mt-7 border-t border-slate-200 pt-6"><button type="button" onClick={() => navigate('/setup-admin')} className="flex w-full items-center justify-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-950 transition"><KeyRound className="h-4 w-4" /> First-time administrator setup</button><p className="mt-4 text-center text-xs text-slate-400">Protected Fortellus production environment</p></div>
        </div>
      </section>
    </main>
  );
}
