import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ERPModules from './pages/ERPModules';
import Personnel from './pages/Personnel';
import ClientsView from './pages/ClientsView';
import SitesView from './pages/SitesView';
import RosterView from './pages/RosterView';
import AttendanceView from './pages/AttendanceView';
import InvoicesView from './pages/InvoicesView';
import './App.css';

function RootRedirect() {
  const { isAuthenticated } = useAuth();
  return <Navigate to={isAuthenticated ? '/erp' : '/login'} replace />;
}

function Protected({ children }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/erp" element={<Protected><ERPModules /></Protected>} />
          <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
          <Route path="/personnel" element={<Protected><Personnel /></Protected>} />
          <Route path="/clients" element={<Protected><ClientsView /></Protected>} />
          <Route path="/sites" element={<Protected><SitesView /></Protected>} />
          <Route path="/rosters" element={<Protected><RosterView /></Protected>} />
          <Route path="/attendance" element={<Protected><AttendanceView /></Protected>} />
          <Route path="/billing" element={<Protected><InvoicesView /></Protected>} />
          <Route path="/" element={<RootRedirect />} />
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
