import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import AdminSetup from './pages/AdminSetup';
import Dashboard from './pages/Dashboard';
import ERPModules from './pages/ERPModules';
import Employees from './pages/Employees';
import Personnel from './pages/Personnel';
import Clients from './pages/Clients';
import Sites from './pages/Sites';
import Rosters from './pages/Rosters';
import Attendance from './pages/Attendance';
import ControlCenter from './pages/ControlCenter';
import ClientsView from './pages/ClientsView';
import SitesView from './pages/SitesView';
import RosterView from './pages/RosterView';
import AttendanceView from './pages/AttendanceView';
import InvoicesView from './pages/InvoicesView';
import './App.css';
import OwnerExecutiveView from './pages/OwnerExecutiveView';

const INTERNAL = ['OWNER','SUPER_ADMIN','ADMIN'];
const HR_ROLES = [...INTERNAL, 'HR'];
const OPS_ROLES = [...INTERNAL, 'OPERATIONS', 'SUPERVISOR'];
const ACCOUNTS_ROLES = [...INTERNAL, 'ACCOUNTS'];
const CLIENT_ROLES = [...INTERNAL, 'CLIENT'];
const STAFF_ROLES = [...CLIENT_ROLES, 'STAFF'];
const ATTENDANCE_ROLES = [...HR_ROLES, 'OPERATIONS', 'SUPERVISOR', 'CLIENT', 'STAFF'];


function RootRedirect() { const { isAuthenticated } = useAuth(); return <Navigate to={isAuthenticated ? '/erp' : '/login'} replace />; }
function Protected({ children, allowedRoles }) { return <ProtectedRoute allowedRoles={allowedRoles}>{children}</ProtectedRoute>; }

function App() {
  return <Router><AuthProvider><Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/setup-admin" element={<AdminSetup />} />
    <Route path="/erp" element={<Protected><ERPModules /></Protected>} />
    <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
    <Route path="/employees" element={<Protected allowedRoles={HR_ROLES}><Employees /></Protected>} />
    <Route path="/personnel" element={<Protected allowedRoles={HR_ROLES}><Personnel /></Protected>} />
    <Route path="/clients" element={<Protected allowedRoles={STAFF_ROLES}><Clients /></Protected>} />
    <Route path="/sites" element={<Protected allowedRoles={STAFF_ROLES}><Sites /></Protected>} />
    <Route path="/rosters" element={<Protected allowedRoles={STAFF_ROLES}><Rosters /></Protected>} />
    <Route path="/attendance" element={<Protected allowedRoles={ATTENDANCE_ROLES}><Attendance /></Protected>} />
    <Route path="/billing" element={<Protected allowedRoles={[...ACCOUNTS_ROLES, 'CLIENT']}><InvoicesView /></Protected>} />
    <Route path="/payroll" element={<Protected allowedRoles={[...ACCOUNTS_ROLES, 'HR']}><ControlCenter type="payroll" /></Protected>} />
    <Route path="/accounts" element={<Protected allowedRoles={ACCOUNTS_ROLES}><ControlCenter type="accounts" /></Protected>} />
    <Route path="/compliance" element={<Protected allowedRoles={[...HR_ROLES, 'ACCOUNTS']}><ControlCenter type="compliance" /></Protected>} />
    <Route path="/risks" element={<Protected allowedRoles={[...INTERNAL, 'HR', 'OPERATIONS', 'ACCOUNTS']}><ControlCenter type="risks" /></Protected>} />
    <Route path="/owner-executive" element={<Protected allowedRoles={['OWNER']}><OwnerExecutiveView /></Protected>} />
    <Route path="/" element={<RootRedirect />} /><Route path="*" element={<RootRedirect />} />
  </Routes></AuthProvider></Router>;
}
export default App;
