import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { rulesAPI } from '../services/api';
import { DomainBadge } from '../components/DomainBadge';
import { StatusBadge } from '../components/StatusBadge';
import type { KnowledgeRule } from '../types';
import './KnowledgeRules.css';

export const KnowledgeRules: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [rules, setRules] = useState<KnowledgeRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [lastPage, setLastPage] = useState(1);
  const [total, setTotal] = useState(0);

  // Filters
  const [search, setSearch] = useState('');
  const [domain, setDomain] = useState<string>('all');
  const [visibility, setVisibility] = useState<string>('all');
  const [status, setStatus] = useState<string>('all');

  // Detail drawer
  const [selectedRule, setSelectedRule] = useState<KnowledgeRule | null>(null);

  // Fetch rules
  useEffect(() => {
    const fetchRules = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = {
          page: currentPage,
          search: search || undefined,
          domain: domain !== 'all' ? domain : undefined,
          visibility: visibility !== 'all' ? visibility : undefined,
          status: status !== 'all' ? status : undefined,
        };

        const response = await rulesAPI.list(
          params.page,
          params.search,
          params.domain,
          params.visibility,
          params.status
        );

        setRules(response.data.data);
        setCurrentPage(response.data.current_page);
        setLastPage(response.data.last_page);
        setTotal(response.data.total);
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to fetch rules');
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  }, [currentPage, search, domain, visibility, status]);

  const isActive = (path: string) => location.pathname === path ? 'active' : '';

  // Truncate text with ellipsis
  const truncateText = (text: string, maxLength: number) => {
    if (text.length > maxLength) {
      return text.substring(0, maxLength) + '...';
    }
    return text;
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Format confidence as percentage
  const formatConfidence = (score: number) => {
    return Math.round(score * 100) + '%';
  };

  // Handle filter reset
  const handleResetFilters = () => {
    setSearch('');
    setDomain('all');
    setVisibility('all');
    setStatus('all');
    setCurrentPage(1);
  };

  return (
    <div className="knowledge-rules-container">
      {/* Sidebar Navigation */}
      <div className="knowledge-rules-sidebar">
        <div className="knowledge-rules-sidebar-title">
          <h3>Menu</h3>
        </div>
        <ul className="knowledge-rules-sidebar-menu">
          <li className="knowledge-rules-sidebar-item">
            <a href="/dashboard" className={`knowledge-rules-sidebar-link ${isActive('/dashboard')}`}>
              Dashboard
            </a>
          </li>
          <li className="knowledge-rules-sidebar-item">
            <a href="/rules" className={`knowledge-rules-sidebar-link ${isActive('/rules')}`}>
              Knowledge Rules
            </a>
          </li>
          <li className="knowledge-rules-sidebar-item">
            <a href="/facts" className={`knowledge-rules-sidebar-link ${isActive('/facts')}`}>
              Knowledge Facts
            </a>
          </li>
          {user?.role === 'admin' && (
            <li className="knowledge-rules-sidebar-item">
              <a href="/upload" className={`knowledge-rules-sidebar-link ${isActive('/upload')}`}>
                Upload
              </a>
            </li>
          )}
        </ul>
      </div>

      {/* Main Content */}
      <div className="knowledge-rules-main">
        {/* Header */}
        <div className="knowledge-rules-header">
          <h1>Knowledge Rules</h1>
          <div className="knowledge-rules-header-info">
            <span className="knowledge-rules-count-badge">
              {total} {total === 1 ? 'rule' : 'rules'}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="knowledge-rules-content">
          {/* Filter Bar */}
          <div className="knowledge-rules-filter-bar">
            <div className="knowledge-rules-filter-grid">
              {/* Search */}
              <div className="knowledge-rules-filter-group">
                <label>Search</label>
                <input
                  type="text"
                  placeholder="Search by source text..."
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setCurrentPage(1);
                  }}
                />
              </div>

              {/* Domain Filter */}
              <div className="knowledge-rules-filter-group">
                <label>Domain</label>
                <select
                  value={domain}
                  onChange={(e) => {
                    setDomain(e.target.value);
                    setCurrentPage(1);
                  }}
                >
                  <option value="all">All</option>
                  <option value="social">Social</option>
                  <option value="economy">Economy</option>
                  <option value="infrastructure">Infrastructure</option>
                  <option value="health">Health</option>
                  <option value="culture_art">Culture & Art</option>
                </select>
              </div>

              {/* Visibility Filter (admin only) */}
              {user?.role === 'admin' && (
                <div className="knowledge-rules-filter-group">
                  <label>Visibility</label>
                  <select
                    value={visibility}
                    onChange={(e) => {
                      setVisibility(e.target.value);
                      setCurrentPage(1);
                    }}
                  >
                    <option value="all">All</option>
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                  </select>
                </div>
              )}

              {/* Status Filter */}
              <div className="knowledge-rules-filter-group">
                <label>Status</label>
                <select
                  value={status}
                  onChange={(e) => {
                    setStatus(e.target.value);
                    setCurrentPage(1);
                  }}
                >
                  <option value="all">All</option>
                  <option value="validated">Validated</option>
                  <option value="pending_review">Pending Review</option>
                </select>
              </div>

              {/* Reset Button */}
              <div className="knowledge-rules-filter-group">
                <button onClick={handleResetFilters}>Reset</button>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && <div className="knowledge-rules-error">{error}</div>}

          {/* Loading State */}
          {loading && (
            <div className="knowledge-rules-loading">
              <div className="knowledge-rules-loading-spinner"></div>
              <p>Loading rules...</p>
            </div>
          )}

          {/* Table */}
          {!loading && rules.length > 0 && (
            <div className="knowledge-rules-table-container">
              <table className="knowledge-rules-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Source Text</th>
                    <th>Domain</th>
                    <th>Visibility</th>
                    <th>Status</th>
                    <th>Confidence</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((rule, index) => (
                    <tr key={rule.id} onClick={() => setSelectedRule(rule)} style={{backgroundColor: index % 2 === 0 ? '#ffffff' : '#f9fafb'}}>
                      <td className="knowledge-rules-table-id">{rule.id}</td>
                      <td className="knowledge-rules-table-source" title={rule.source_text}>
                        {truncateText(rule.source_text, 60)}
                      </td>
                      <td>
                        <DomainBadge domain={rule.domain} />
                      </td>
                      <td>
                        <span className={`knowledge-rules-table-badge knowledge-rules-visibility-${rule.visibility}`}>
                          {rule.visibility.charAt(0).toUpperCase() + rule.visibility.slice(1)}
                        </span>
                      </td>
                      <td>
                        <StatusBadge status={rule.status} />
                      </td>
                      <td>{formatConfidence(rule.confidence_score)}</td>
                      <td>{formatDate(rule.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Empty State */}
          {!loading && rules.length === 0 && (
            <div className="knowledge-rules-empty">
              <p>No rules found</p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {!loading && rules.length > 0 && (
          <div className="knowledge-rules-pagination">
            <div className="knowledge-rules-pagination-info">
              Page {currentPage} of {lastPage}
            </div>
            <div className="knowledge-rules-pagination-buttons">
              <button
                className="knowledge-rules-pagination-btn"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              <button
                className="knowledge-rules-pagination-btn"
                onClick={() => setCurrentPage(Math.min(lastPage, currentPage + 1))}
                disabled={currentPage === lastPage}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Drawer Overlay */}
      {selectedRule && <div className="knowledge-rules-overlay" onClick={() => setSelectedRule(null)}></div>}

      {/* Detail Drawer */}
      {selectedRule && (
        <div className="knowledge-rules-drawer">
          {/* Header */}
          <div className="knowledge-rules-drawer-header">
            <h3>Rule Details</h3>
            <button className="knowledge-rules-drawer-close" onClick={() => setSelectedRule(null)}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="knowledge-rules-drawer-content">
            {/* Source Text */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Source Text</div>
              <div className="knowledge-rules-drawer-value">
                {selectedRule.source_text}
              </div>
            </div>

            {/* Domain */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Domain</div>
              <div style={{marginTop: '0.5rem'}}>
                <DomainBadge domain={selectedRule.domain} />
              </div>
            </div>

            {/* Visibility */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Visibility</div>
              <div style={{marginTop: '0.5rem'}}>
                <span className={`knowledge-rules-table-badge knowledge-rules-visibility-${selectedRule.visibility}`}>
                  {selectedRule.visibility.charAt(0).toUpperCase() + selectedRule.visibility.slice(1)}
                </span>
              </div>
            </div>

            {/* Status */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Status</div>
              <div style={{marginTop: '0.5rem'}}>
                <StatusBadge status={selectedRule.status} />
              </div>
            </div>

            {/* Confidence */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Confidence Score</div>
              <div className="knowledge-rules-drawer-value">
                {formatConfidence(selectedRule.confidence_score)}
              </div>
            </div>

            {/* Extraction Method */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Extraction Method</div>
              <div className="knowledge-rules-drawer-value">
                {selectedRule.extraction_method.toUpperCase()}
              </div>
            </div>

            {/* Algorithm Used */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Algorithm Used</div>
              <div className="knowledge-rules-drawer-value">
                {selectedRule.algorithm_used || 'N/A'}
              </div>
            </div>

            {/* Created At */}
            <div className="knowledge-rules-drawer-field">
              <div className="knowledge-rules-drawer-label">Created At</div>
              <div className="knowledge-rules-drawer-value">
                {new Date(selectedRule.created_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="knowledge-rules-drawer-footer">
            <button onClick={() => setSelectedRule(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};
