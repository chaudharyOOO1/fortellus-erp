import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { Lock, Mail, Loader2, ShieldCheck, ArrowRight, KeyRound } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('admin@fortelluserp.com');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard', { replace: true });
  }, [isAuthenticated, navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const result = await login(email, password);
    if (result.success) navigate('/dashboard');
    else setError(result.error);
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-[#f5f7fb]">
      <div className="w-full max-w-md bg-white rounded-3xl p-8 border border-slate-200 shadow-xl space-y-6">
        <div className="text-center">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 mb-4">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Fortellus ERP</h1>
          <p className="text-sm font-semibold text-slate-600 mt-1">Administrator Login</p>
          <p className="text-xs text-slate-400 mt-1">Secure enterprise operations portal</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-semibold text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Administrator email</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-teal-600" />
              <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                placeholder="admin@fortelluserp.com" className="w-full cyber-input pl-10 h-11" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Administrator password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-teal-600" />
              <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password" className="w-full cyber-input pl-10 h-11" />
            </div>
          </div>

          <button type="submit" disabled={loading}
            className="w-full h-11 rounded-xl bg-teal-700 hover:bg-teal-800 text-white font-bold transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-50">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>Sign in <ArrowRight className="w-4 h-4" /></>}
          </button>
        </form>

        <div className="pt-4 border-t border-slate-200 text-center space-y-2">
          <button type="button" onClick={() => navigate('/setup-admin')}
            className="mx-auto flex items-center gap-2 text-sm font-semibold text-teal-700 hover:text-teal-800">
            <KeyRound className="w-4 h-4" /> First-time administrator setup
          </button>
          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-mono font-bold">
            Production administrator access
          </p>
        </div>
      </div>
    </div>
  );
}
