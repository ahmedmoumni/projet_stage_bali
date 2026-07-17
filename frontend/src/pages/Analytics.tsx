import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { analyticsAPI } from '../services/api';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import './Analytics.css';

interface MonthlyData {
  month: string;
  rules: number;
  facts: number;
}

interface MethodsData {
  extraction: {
    spacy: number;
    llm: number;
  };
  algorithm: {
    naive_bayes: number;
    decision_tree: number;
  };
}

interface DocumentLog {
  id: number;
  filename: string;
  file_type: string;
  routing: string;
  pages: number;
  rules_extracted: number;
  facts_extracted: number;
  processed_at: string;
}

interface PaginatedDocuments {
  data: DocumentLog[];
  current_page: number;
  last_page: number;
  total: number;
  per_page: number;
}

const getFileTypeBadge = (fileType: string) => {
  switch (fileType) {
    case 'pdf_native':
      return 'bg-blue-100 text-blue-800';
    case 'pdf_scanned':
      return 'bg-sky-100 text-sky-800';
    case 'csv':
      return 'bg-emerald-100 text-emerald-800';
    case 'excel':
      return 'bg-lime-100 text-lime-800';
    default:
      return 'bg-slate-100 text-slate-700';
  }
};

const getRoutingBadge = (routing: string) => {
  switch (routing) {
    case 'rejected':
      return 'bg-red-100 text-red-800';
    case 'pipeline1':
      return 'bg-indigo-100 text-indigo-800';
    case 'pipeline2_direct':
      return 'bg-teal-100 text-teal-800';
    case 'ocr_then_pipeline1':
      return 'bg-orange-100 text-orange-800';
    default:
      return 'bg-slate-100 text-slate-700';
  }
};

export const Analytics = () => {
  const { user, isLoading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [methodsData, setMethodsData] = useState<MethodsData>({
    extraction: { spacy: 0, llm: 0 },
    algorithm: { naive_bayes: 0, decision_tree: 0 },
  });
  const [documents, setDocuments] = useState<PaginatedDocuments | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  useEffect(() => {
    if (!isLoading && user && user.role !== 'admin') {
      navigate('/dashboard');
    }
  }, [isLoading, user, navigate]);

  useEffect(() => {
    if (!user) {
      return;
    }

    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);

        const [monthlyResponse, methodsResponse, documentsResponse] = await Promise.all([
          analyticsAPI.monthly(),
          analyticsAPI.methods(),
          analyticsAPI.documents(page),
        ]);

        setMonthlyData(monthlyResponse.data);
        setMethodsData(methodsResponse.data);
        setDocuments(documentsResponse.data);
      } catch (err) {
        console.error('Analytics fetch failed:', err);
        setError(err instanceof Error ? err.message : 'Unable to load analytics data.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [user, page]);

  const isActive = (path: string) => (location.pathname === path ? 'active' : '');

  const extractionChartData = useMemo(
    () => [
      { name: 'spaCy', value: methodsData.extraction.spacy },
      { name: 'LLM', value: methodsData.extraction.llm },
    ],
    [methodsData]
  );

  const algorithmChartData = useMemo(
    () => [
      { name: 'Naive Bayes', value: methodsData.algorithm.naive_bayes },
      { name: 'Decision Tree', value: methodsData.algorithm.decision_tree },
    ],
    [methodsData]
  );

  return (
    <div className="dashboard-container">
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
            </>
          )}
        </ul>
      </div>

      <div className="dashboard-main">
        <div className="dashboard-header">
          <div className={`dashboard-role-badge ${user?.role === 'admin' ? 'admin' : 'user'}`}>
            {user?.role?.toUpperCase()}
          </div>
          <button onClick={handleLogout} className="dashboard-logout-btn">
            Logout
          </button>
        </div>

        <div className="dashboard-content">
          {loading ? (
            <div className="dashboard-loading">
              <div className="loading-spinner"></div>
              <p>Loading analytics...</p>
            </div>
          ) : error ? (
            <div className="dashboard-error">
              <p>Error: {error}</p>
            </div>
          ) : (
            <>
              <div className="dashboard-stats-section">
                <h2 className="dashboard-title">Knowledge Extracted per Month</h2>
                <div className="bg-white rounded-3xl p-6 shadow-sm">
                  <ResponsiveContainer width="100%" height={320}>
                    <LineChart data={monthlyData} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" stroke="#0f172a" />
                      <YAxis stroke="#0f172a" allowDecimals={false} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="rules" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />
                      <Line type="monotone" dataKey="facts" stroke="#14b8a6" strokeWidth={3} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="dashboard-stats-grid">
                <div className="bg-white rounded-3xl p-6 shadow-sm">
                  <h3 className="text-xl font-semibold text-slate-900 mb-4">Extraction Method</h3>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={extractionChartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" stroke="#0f172a" />
                      <YAxis stroke="#0f172a" allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#2563eb" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="bg-white rounded-3xl p-6 shadow-sm">
                  <h3 className="text-xl font-semibold text-slate-900 mb-4">Algorithm Used</h3>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={algorithmChartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" stroke="#0f172a" />
                      <YAxis stroke="#0f172a" allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#14b8a6" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="dashboard-info-section">
                <div className="dashboard-info-card">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between mb-6">
                    <div>
                      <h3 className="text-xl font-semibold text-slate-900">Document Log</h3>
                      <p className="text-sm text-slate-500">Document logs with pagination.</p>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                      <thead className="bg-slate-50 text-slate-500 uppercase text-xs tracking-wider">
                        <tr>
                          <th className="px-4 py-3">Filename</th>
                          <th className="px-4 py-3">File Type</th>
                          <th className="px-4 py-3">Routing</th>
                          <th className="px-4 py-3">Pages</th>
                          <th className="px-4 py-3">Rules</th>
                          <th className="px-4 py-3">Facts</th>
                          <th className="px-4 py-3">Date</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200">
                        {documents?.data.length ? (
                          documents.data.map((document) => (
                            <tr key={document.id} className="bg-white">
                              <td className="px-4 py-4 text-slate-700">{document.filename}</td>
                              <td className="px-4 py-4">
                                <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${getFileTypeBadge(document.file_type)}`}>
                                  {document.file_type}
                                </span>
                              </td>
                              <td className="px-4 py-4">
                                <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${getRoutingBadge(document.routing)}`}>
                                  {document.routing}
                                </span>
                              </td>
                              <td className="px-4 py-4 text-slate-700">{document.pages}</td>
                              <td className="px-4 py-4 text-slate-700">{document.rules_extracted}</td>
                              <td className="px-4 py-4 text-slate-700">{document.facts_extracted}</td>
                              <td className="px-4 py-4 text-slate-700">
                                {new Date(document.processed_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                              No document logs found for the selected filters.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <span className="text-sm text-slate-500">
                      Page {documents?.current_page ?? 1} of {documents?.last_page ?? 1}
                    </span>
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                        onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                        disabled={!documents || documents.current_page <= 1}
                      >
                        Previous
                      </button>
                      <button
                        type="button"
                        className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                        onClick={() => setPage((prev) => (documents ? Math.min(prev + 1, documents.last_page) : prev + 1))}
                        disabled={!documents || documents.current_page >= documents.last_page}
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
