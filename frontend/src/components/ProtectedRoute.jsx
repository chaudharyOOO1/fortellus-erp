import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function ProtectedRoute({ children, allowedRoles = null }) {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { replace: true, state: { from: location.pathname } });
    }
  }, [isAuthenticated, navigate, location.pathname]);

  if (!isAuthenticated) return null;

  if (Array.isArray(allowedRoles) && allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-rose-500">403 Forbidden</div>
          <h1 className="mt-3 text-2xl font-semibold text-slate-900">Access restricted</h1>
          <p className="mt-2 text-sm leading-6 text-slate-500">Your current role does not have permission to open this workspace.</p>
          <button onClick={() => navigate('/dashboard', { replace: true })} className="mt-6 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800">Return to dashboard</button>
        </div>
      </div>
    );
  }

  return children;
}
