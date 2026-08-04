import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { StatCard } from '../components/StatCard';
import './Dashboard.css';

// TypeScript Interfaces
interface DashboardStats {
  total_rules: number;
  total_facts: number;
  total_validated: number;
  total_pending: number;
  total_documents: number;
}

// Icons
const RulesIcon = () => <span></span>;
const FactsIcon = () => <span></span>;
const ValidatedIcon = () => <span></span>;
const PendingIcon = () => <span></span>;

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('auth_token');
        
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/dashboard`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch dashboard stats');
        }

        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

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
          <li className="dashboard-sidebar-item">
            <a href="/rules" className={`dashboard-sidebar-link ${isActive('/rules')}`}>
              Knowledge Rules
            </a>
          </li>
          <li className="dashboard-sidebar-item">
            <a href="/facts" className={`dashboard-sidebar-link ${isActive('/facts')}`}>
              Knowledge Facts
            </a>
          </li>
          {user?.role === 'admin' && (
            <>
              <li className="dashboard-sidebar-item">
                <a href="/analytics" className={`dashboard-sidebar-link ${isActive('/analytics')}`}>
                  Analytics
                </a>
              </li>
              <li className="dashboard-sidebar-item">
                <a href="/pending-review" className={`dashboard-sidebar-link ${isActive('/pending-review')}`}>
                  Pending Review
                </a>
              </li>
              <li className="dashboard-sidebar-item">
                <a href="/upload" className={`dashboard-sidebar-link ${isActive('/upload')}`}>
                  Upload
                </a>
              </li>
              <li className="dashboard-sidebar-item">
                <a href="/upload-csv" className={`dashboard-sidebar-link ${isActive('/upload-csv')}`}>
                  Rule Discovery
                </a>
              </li>
            </>
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
            Logout
          </button>
        </div>

        {/* Content */}
        <div className="dashboard-content">
          {loading ? (
            <div className="dashboard-loading">
              <div className="loading-spinner"></div>
              <p>Loading dashboard...</p>
            </div>
          ) : error ? (
            <div className="dashboard-error">
              <p>Error: {error}</p>
            </div>
          ) : stats ? (
            <>
              {/* Stat Cards Section */}
              <div className="dashboard-stats-section">
                <h2 className="dashboard-title">Dashboard Overview</h2>
                <div className="dashboard-stats-grid">
                  <StatCard
                    icon={<RulesIcon />}
                    label="Total Rules"
                    value={stats.total_rules}
                    variant="blue"
                  />
                  <StatCard
                    icon={<FactsIcon />}
                    label="Total Facts"
                    value={stats.total_facts}
                    variant="teal"
                  />
                  <StatCard
                    icon={<ValidatedIcon />}
                    label="Total Validated"
                    value={stats.total_validated}
                    variant="green"
                  />
                  {user?.role === 'admin' && (
                    <StatCard
                      icon={<PendingIcon />}
                      label="Total Pending"
                      value={stats.total_pending}
                      variant="orange"
                    />
                  )}
                </div>
              </div>

              {/* Additional Info Section */}
              <div className="dashboard-info-section">
                <div className="dashboard-info-card">
                  <h3> Documents</h3>
                  <p className="dashboard-info-value">{stats.total_documents}</p>
                  <p className="dashboard-info-label">Documents Uploaded</p>
                </div>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};
