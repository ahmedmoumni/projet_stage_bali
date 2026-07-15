import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { pendingAPI } from '../services/api';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { EditModal } from '../components/EditModal';
import { DomainBadge } from '../components/DomainBadge';
import { useAuth } from '../api/AuthContext';
import type { PendingItem, EditPayload } from '../types/index';
import './PendingReview.css';

export const PendingReview: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [items, setItems] = useState<PendingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [lastPage, setLastPage] = useState(1);

  const [typeFilter, setTypeFilter] = useState<'all' | 'rule' | 'fact'>('all');
  const [domainFilter, setDomainFilter] = useState<string>('all');

  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    action: 'approve' | 'reject' | null;
    item: PendingItem | null;
  }>({
    isOpen: false,
    action: null,
    item: null,
  });

  const [editModal, setEditModal] = useState<{
    isOpen: boolean;
    item: PendingItem | null;
  }>({
    isOpen: false,
    item: null,
  });

  const [editLoading, setEditLoading] = useState(false);

  // Redirect if not admin
  useEffect(() => {
    if (user && user.role !== 'admin') {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  // Load pending items
  useEffect(() => {
    loadPendingItems();
  }, [page, typeFilter, domainFilter]);

  const loadPendingItems = async () => {
    setLoading(true);
    try {
      const response = await pendingAPI.list(
        page,
        typeFilter === 'all' ? undefined : typeFilter,
        domainFilter === 'all' ? undefined : domainFilter
      );
      setItems(response.data.data);
      setTotalItems(response.data.total);
      setLastPage(response.data.last_page);
    } catch (error) {
      console.error('Failed to load pending items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveClick = (item: PendingItem) => {
    setConfirmDialog({
      isOpen: true,
      action: 'approve',
      item,
    });
  };

  const handleRejectClick = (item: PendingItem) => {
    setConfirmDialog({
      isOpen: true,
      action: 'reject',
      item,
    });
  };

  const handleEditClick = (item: PendingItem) => {
    setEditModal({
      isOpen: true,
      item,
    });
  };

  const handleConfirmApprove = async () => {
    if (!confirmDialog.item) return;

    try {
      await pendingAPI.approve(confirmDialog.item.type, confirmDialog.item.id);
      setItems(items.filter((i) => i.id !== confirmDialog.item!.id));
      setConfirmDialog({ isOpen: false, action: null, item: null });
    } catch (error) {
      console.error('Failed to approve item:', error);
    }
  };

  const handleConfirmReject = async () => {
    if (!confirmDialog.item) return;

    try {
      await pendingAPI.reject(confirmDialog.item.type, confirmDialog.item.id);
      setItems(items.filter((i) => i.id !== confirmDialog.item!.id));
      setConfirmDialog({ isOpen: false, action: null, item: null });
    } catch (error) {
      console.error('Failed to reject item:', error);
    }
  };

  const handleSaveEdit = async (data: EditPayload) => {
    if (!editModal.item) return;

    setEditLoading(true);
    try {
      const response = await pendingAPI.update(editModal.item.type, editModal.item.id, data);
      
      // Update the item in the list
      setItems(items.map((item) =>
        item.id === editModal.item!.id && item.type === editModal.item!.type
          ? { ...item, ...response.data.data }
          : item
      ));

      setEditModal({ isOpen: false, item: null });
    } catch (error) {
      console.error('Failed to update item:', error);
    } finally {
      setEditLoading(false);
    }
  };

  const truncateText = (text: string, length: number) => {
    if (text.length > length) {
      return text.substring(0, length) + '...';
    }
    return text;
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= lastPage) {
      setPage(newPage);
      window.scrollTo(0, 0);
    }
  };

  return (
    <div className="pending-review-container">
      {/* Sidebar */}
      <aside className="pending-review-sidebar">
        <div className="pending-review-sidebar-logo">
          <div className="pending-review-logo-text">Menu</div>
        </div>

        <ul className="pending-review-sidebar-menu">
          <li className="pending-review-sidebar-item">
            <a href="/dashboard" className="pending-review-sidebar-link">
              Dashboard
            </a>
          </li>
          <li className="pending-review-sidebar-item">
            <a href="/rules" className="pending-review-sidebar-link">
              Knowledge Rules
            </a>
          </li>
          <li className="pending-review-sidebar-item">
            <a href="/facts" className="pending-review-sidebar-link">
              Knowledge Facts
            </a>
          </li>
          <li className="pending-review-sidebar-item">
            <a href="/pending-review" className="pending-review-sidebar-link active">
              Pending Review
            </a>
          </li>
          {user?.role === 'admin' && (
            <li className="pending-review-sidebar-item">
              <a href="/upload" className="pending-review-sidebar-link">
                Upload
              </a>
            </li>
          )}
        </ul>
      </aside>

      {/* Main Content */}
      <main className="pending-review-main">
        {/* Header */}
        <div className="pending-review-header">
          <div className="pending-review-header-title">
            <h1>Pending Review</h1>
            <div className="pending-review-count-badge">{totalItems}</div>
          </div>
        </div>

        {/* Main Content */}
        <div className="pending-review-content">
          {/* Filters */}
          <div className="pending-review-filters">
          <div className="pending-review-filter-group">
            <label className="pending-review-filter-label">Type</label>
            <select
              className="pending-review-filter-select"
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value as 'all' | 'rule' | 'fact');
                setPage(1);
              }}
            >
              <option value="all">All</option>
              <option value="rule">Rules</option>
              <option value="fact">Facts</option>
            </select>
          </div>

          <div className="pending-review-filter-group">
            <label className="pending-review-filter-label">Domain</label>
            <select
              className="pending-review-filter-select"
              value={domainFilter}
              onChange={(e) => {
                setDomainFilter(e.target.value);
                setPage(1);
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
        </div>

        {/* Table */}
        {loading ? (
          <div className="pending-review-loading">Loading...</div>
        ) : items.length === 0 ? (
          <div className="pending-review-empty">No pending items</div>
        ) : (
          <>
            <div className="pending-review-table-wrapper">
              <table className="pending-review-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Source Text</th>
                    <th>Domain</th>
                    <th>Confidence</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={`${item.type}-${item.id}`}>
                      <td className="pending-review-cell-id">{item.id}</td>
                      <td>
                        <span className={`pending-review-type-badge pending-review-type-${item.type}`}>
                          {item.type === 'rule' ? 'Rule' : 'Fact'}
                        </span>
                      </td>
                      <td className="pending-review-cell-text">
                        {truncateText(item.source_text, 60)}
                      </td>
                      <td>
                        {item.domain ? (
                          <DomainBadge domain={item.domain} />
                        ) : (
                          <span className="pending-review-domain-unclassified">Unclassified</span>
                        )}
                      </td>
                      <td className="pending-review-cell-confidence">
                        {(item.confidence_score * 100).toFixed(0)}%
                      </td>
                      <td className="pending-review-cell-date">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td className="pending-review-cell-actions">
                        <button
                          className="pending-review-btn-approve"
                          onClick={() => handleApproveClick(item)}
                          title="Approve"
                        >
                          Approve
                        </button>
                        <button
                          className="pending-review-btn-edit"
                          onClick={() => handleEditClick(item)}
                          title="Edit"
                        >
                          Edit
                        </button>
                        <button
                          className="pending-review-btn-reject"
                          onClick={() => handleRejectClick(item)}
                          title="Reject"
                        >
                          Reject
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="pending-review-pagination">
              <button
                className="pending-review-pagination-btn"
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
              >
                Previous
              </button>

              <span className="pending-review-pagination-info">
                Page {page} of {lastPage}
              </span>

              <button
                className="pending-review-pagination-btn"
                onClick={() => handlePageChange(page + 1)}
                disabled={page === lastPage}
              >
                Next
              </button>
            </div>
          </>
        )}
        </div>
      </main>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.action === 'approve' ? 'Approve Item' : 'Reject Item'}
        message={
          confirmDialog.action === 'approve'
            ? 'Are you sure you want to approve this item?'
            : 'Reject and permanently delete this item?'
        }
        confirmText={confirmDialog.action === 'approve' ? 'Approve' : 'Reject'}
        isDangerous={confirmDialog.action === 'reject'}
        onConfirm={confirmDialog.action === 'approve' ? handleConfirmApprove : handleConfirmReject}
        onCancel={() => setConfirmDialog({ isOpen: false, action: null, item: null })}
      />

      {/* Edit Modal */}
      <EditModal
        isOpen={editModal.isOpen}
        item={editModal.item}
        onClose={() => setEditModal({ isOpen: false, item: null })}
        onSave={handleSaveEdit}
        isLoading={editLoading}
      />
    </div>
  );
};

export default PendingReview;
