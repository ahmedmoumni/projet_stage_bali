import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { factsAPI } from '../services/api';
import { DomainBadge } from '../components/DomainBadge';
import { StatusBadge } from '../components/StatusBadge';
import type { KnowledgeFact, FactValue } from '../types';
import './KnowledgeFacts.css';

export const KnowledgeFacts: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [facts, setFacts] = useState<KnowledgeFact[]>([]);
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
  const [selectedFact, setSelectedFact] = useState<KnowledgeFact | null>(null);

  // Fetch facts
  useEffect(() => {
    const fetchFacts = async () => {
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

        const response = await factsAPI.list(
          params.page,
          params.search,
          params.domain,
          params.visibility,
          params.status
        );

        setFacts(response.data.data);
        setCurrentPage(response.data.current_page);
        setLastPage(response.data.last_page);
        setTotal(response.data.total);
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to fetch facts');
      } finally {
        setLoading(false);
      }
    };

    fetchFacts();
  }, [currentPage, search, domain, visibility, status]);

  const isActive = (path: string) => location.pathname === path ? 'active' : '';

  // Format values for display
  const formatValues = (values: FactValue[]) => {
    if (!values || values.length === 0) {
      return 'N/A';
    }

    const formattedValues = values.map((val) => {
      if (val.value_type === 'continuous') {
        return `${val.value_continuous}${val.unit ? ' ' + val.unit : ''}`;
      } else {
        return val.value_categorical || 'N/A';
      }
    });

    if (formattedValues.length <= 3) {
      return formattedValues.join(', ');
    } else {
      return `${formattedValues.slice(0, 3).join(', ')} +${formattedValues.length - 3} more`;
    }
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
    <div className="knowledge-facts-container">
      {/* Sidebar Navigation */}
      <div className="knowledge-facts-sidebar">
        <div className="knowledge-facts-sidebar-title">
          <h3>Menu</h3>
        </div>
        <ul className="knowledge-facts-sidebar-menu">
          <li className="knowledge-facts-sidebar-item">
            <a href="/dashboard" className={`knowledge-facts-sidebar-link ${isActive('/dashboard')}`}>
              Dashboard
            </a>
          </li>
          <li className="knowledge-facts-sidebar-item">
            <a href="/rules" className={`knowledge-facts-sidebar-link ${isActive('/rules')}`}>
              Knowledge Rules
            </a>
          </li>
          <li className="knowledge-facts-sidebar-item">
            <a href="/facts" className={`knowledge-facts-sidebar-link ${isActive('/facts')}`}>
              Knowledge Facts
            </a>
          </li>
          {user?.role === 'admin' && (
            <li className="knowledge-facts-sidebar-item">
              <a href="/upload" className={`knowledge-facts-sidebar-link ${isActive('/upload')}`}>
                Upload
              </a>
            </li>
          )}
        </ul>
      </div>

      {/* Main Content */}
      <div className="knowledge-facts-main">
        {/* Header */}
        <div className="knowledge-facts-header">
          <h1>Knowledge Facts</h1>
          <div className="knowledge-facts-header-info">
            <span className="knowledge-facts-count-badge">
              {total} {total === 1 ? 'fact' : 'facts'}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="knowledge-facts-content">
          {/* Filter Bar */}
          <div className="knowledge-facts-filter-bar">
            <div className="knowledge-facts-filter-grid">
              {/* Search */}
              <div className="knowledge-facts-filter-group">
                <label>Search</label>
                <input
                  type="text"
                  placeholder="Search by subject or relation..."
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setCurrentPage(1);
                  }}
                />
              </div>

              {/* Domain Filter */}
              <div className="knowledge-facts-filter-group">
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
                <div className="knowledge-facts-filter-group">
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
              <div className="knowledge-facts-filter-group">
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
              <div className="knowledge-facts-filter-group">
                <button onClick={handleResetFilters}>Reset</button>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && <div className="knowledge-facts-error">{error}</div>}

          {/* Loading State */}
          {loading && (
            <div className="knowledge-facts-loading">
              <div className="knowledge-facts-loading-spinner"></div>
              <p>Loading facts...</p>
            </div>
          )}

          {/* Table */}
          {!loading && facts.length > 0 && (
            <div className="knowledge-facts-table-container">
              <table className="knowledge-facts-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Subject</th>
                    <th>Relation</th>
                    <th>Values</th>
                    <th>Domain</th>
                    <th>Visibility</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {facts.map((fact, index) => (
                    <tr key={fact.id} onClick={() => setSelectedFact(fact)} style={{backgroundColor: index % 2 === 0 ? '#ffffff' : '#f9fafb'}}>
                      <td className="knowledge-facts-table-id">{fact.id}</td>
                      <td className="knowledge-facts-table-subject">
                        <strong>{fact.subject}</strong>
                      </td>
                      <td className="knowledge-facts-table-relation">
                        <span style={{color: '#9ca3af', fontStyle: 'italic'}}>{fact.relation}</span>
                      </td>
                      <td className="knowledge-facts-table-values">
                        {formatValues(fact.values)}
                      </td>
                      <td>
                        <DomainBadge domain={fact.domain} />
                      </td>
                      <td>
                        <span className={`knowledge-facts-table-badge knowledge-facts-visibility-${fact.visibility}`}>
                          {fact.visibility.charAt(0).toUpperCase() + fact.visibility.slice(1)}
                        </span>
                      </td>
                      <td>
                        <StatusBadge status={fact.status} />
                      </td>
                      <td>{formatDate(fact.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Empty State */}
          {!loading && facts.length === 0 && (
            <div className="knowledge-facts-empty">
              <p>No facts found</p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {!loading && facts.length > 0 && (
          <div className="knowledge-facts-pagination">
            <div className="knowledge-facts-pagination-info">
              Page {currentPage} of {lastPage}
            </div>
            <div className="knowledge-facts-pagination-buttons">
              <button
                className="knowledge-facts-pagination-btn"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              <button
                className="knowledge-facts-pagination-btn"
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
      {selectedFact && <div className="knowledge-facts-overlay" onClick={() => setSelectedFact(null)}></div>}

      {/* Detail Drawer */}
      {selectedFact && (
        <div className="knowledge-facts-drawer">
          {/* Header */}
          <div className="knowledge-facts-drawer-header">
            <h3>Fact Details</h3>
            <button className="knowledge-facts-drawer-close" onClick={() => setSelectedFact(null)}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="knowledge-facts-drawer-content">
            {/* Source Text */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Source Text</div>
              <div className="knowledge-facts-drawer-value">
                {selectedFact.source_text}
              </div>
            </div>

            {/* Subject */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Subject</div>
              <div className="knowledge-facts-drawer-value">
                <strong>{selectedFact.subject}</strong>
              </div>
            </div>

            {/* Relation */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Relation</div>
              <div className="knowledge-facts-drawer-value">
                <em>{selectedFact.relation}</em>
              </div>
            </div>

            {/* Values */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Values</div>
              <div className="knowledge-facts-drawer-value">
                {selectedFact.values && selectedFact.values.length > 0 ? (
                  <div>
                    {selectedFact.values.map((val, idx) => (
                      <div key={idx} style={{marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid #e5e7eb'}}>
                        <div style={{fontSize: '0.85rem', fontWeight: '600', color: '#374151'}}>
                          {val.value_type === 'continuous' ? 'Continuous' : 'Categorical'}
                        </div>
                        <div style={{fontSize: '0.9rem', color: '#6b7280', marginTop: '0.25rem'}}>
                          {val.value_type === 'continuous' 
                            ? `${val.value_continuous}${val.unit ? ' ' + val.unit : ''}`
                            : val.value_categorical
                          }
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <span>No values</span>
                )}
              </div>
            </div>

            {/* Domain */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Domain</div>
              <div style={{marginTop: '0.5rem'}}>
                <DomainBadge domain={selectedFact.domain} />
              </div>
            </div>

            {/* Visibility */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Visibility</div>
              <div style={{marginTop: '0.5rem'}}>
                <span className={`knowledge-facts-table-badge knowledge-facts-visibility-${selectedFact.visibility}`}>
                  {selectedFact.visibility.charAt(0).toUpperCase() + selectedFact.visibility.slice(1)}
                </span>
              </div>
            </div>

            {/* Status */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Status</div>
              <div style={{marginTop: '0.5rem'}}>
                <StatusBadge status={selectedFact.status} />
              </div>
            </div>

            {/* Confidence */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Confidence Score</div>
              <div className="knowledge-facts-drawer-value">
                {formatConfidence(selectedFact.confidence_score)}
              </div>
            </div>

            {/* Extraction Method */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Extraction Method</div>
              <div className="knowledge-facts-drawer-value">
                {selectedFact.extraction_method.toUpperCase()}
              </div>
            </div>

            {/* Algorithm Used */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Algorithm Used</div>
              <div className="knowledge-facts-drawer-value">
                {selectedFact.algorithm_used || 'N/A'}
              </div>
            </div>

            {/* Created At */}
            <div className="knowledge-facts-drawer-field">
              <div className="knowledge-facts-drawer-label">Created At</div>
              <div className="knowledge-facts-drawer-value">
                {new Date(selectedFact.created_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="knowledge-facts-drawer-footer">
            <button onClick={() => setSelectedFact(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};
