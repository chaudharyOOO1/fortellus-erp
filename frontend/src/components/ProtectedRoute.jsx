import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function ProtectedRoute({ children, allowedRoles = null, permission = null }) {
  const { user, isAuthenticated, can, permissionsLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isAuthenticated) navigate('/login', { replace: true, state: { from: location.pathname } });
    else if (!permissionsLoading && !user?.password_initialized_at && location.pathname !== '/account') navigate('/account', { replace: true });
    else if (!permissionsLoading && permission && !can(permission)) navigate('/account', { replace: true });
    else if (!permissionsLoading && Array.isArray(allowedRoles) && allowedRoles.length && !allowedRoles.includes(user?.role)) navigate('/account', { replace: true });
  }, [isAuthenticated, permissionsLoading, permission, allowedRoles, user, can, navigate, location.pathname]);

  if (!isAuthenticated || permissionsLoading) return null;
  if (permission && !can(permission)) return null;
  if (Array.isArray(allowedRoles) && allowedRoles.length && !allowedRoles.includes(user?.role)) return null;
  return children;
}
