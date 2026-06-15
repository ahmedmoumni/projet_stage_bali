import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import './Dashboard.css';

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (user?.role === 'admin') {
      console.log('Admin connecté');
    } else {
      console.log('User connecté');
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path ? 'active' : '';

  return (
    <div className="dashboard-container">
      {/* Sidebar Navigation */}
      <div className="dashboard-sidebar">
        <div className="dashboard-sidebar-title">
          <h3>Menu</h3>
        </div>
        <ul className="dashboard-sidebar-menu">
          <li className="dashboard-sidebar-item">
            <a href="/dashboard" className={`dashboard-sidebar-link ${isActive('/dashboard')}`}>
              Dashboard
            </a>
          </li>
          {user?.role === 'admin' && (
            <li className="dashboard-sidebar-item">
              <a href="/upload" className={`dashboard-sidebar-link ${isActive('/upload')}`}>
                Upload
              </a>
            </li>
          )}
        </ul>
      </div>

      {/* Main Content */}
      <div className="dashboard-main">
        {/* Header */}
        <div className="dashboard-header">
          <div className={`dashboard-role-badge ${user?.role === 'admin' ? 'admin' : 'user'}`}>
            {user?.role?.toUpperCase()}
          </div>
          <button
            onClick={handleLogout}
            className="dashboard-logout-btn"
          >
            Déconnexion
          </button>
        </div>

        {/* Content */}
        <div className="dashboard-content">
        </div>
      </div>
    </div>
  );
};
