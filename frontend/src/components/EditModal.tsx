import React, { useState, useEffect } from 'react';
import type { Domain, EditPayload } from '../types/index';
import './EditModal.css';

interface EditModalProps {
  isOpen: boolean;
  item: any;
  onClose: () => void;
  onSave: (data: EditPayload) => void;
  isLoading?: boolean;
}

const DOMAINS: Domain[] = ['social', 'economy', 'infrastructure', 'health', 'culture_art'];
const DOMAIN_LABELS: Record<Domain, string> = {
  social: 'Social',
  economy: 'Economy',
  infrastructure: 'Infrastructure',
  health: 'Health',
  culture_art: 'Culture & Art',
};

export const EditModal: React.FC<EditModalProps> = ({
  isOpen,
  item,
  onClose,
  onSave,
  isLoading = false,
}) => {
  const [sourceText, setSourceText] = useState('');
  const [domain, setDomain] = useState<Domain | null>(null);
  const [visibility, setVisibility] = useState<'public' | 'private'>('private');
  const [conditionText, setConditionText] = useState('');
  const [actionText, setActionText] = useState('');
  const [subjectText, setSubjectText] = useState('');
  const [relationText, setRelationText] = useState('');
  const [valuesText, setValuesText] = useState('');

  useEffect(() => {
    if (item) {
      setSourceText(item.source_text || '');
      setDomain(item.domain || null);
      setVisibility(item.visibility || 'private');
      setConditionText((item.conditions || []).map((c: any) => `${c.subject} ${c.operator} ${c.values?.map((v: any) => v.value_categorical ?? v.value_continuous).filter(Boolean).join(', ')}`).join('\n'));
      setActionText((item.actions || []).map((a: any) => `${a.subject} ${a.operator} ${a.values?.map((v: any) => v.value_categorical ?? v.value_continuous).filter(Boolean).join(', ')}`).join('\n'));
      setSubjectText(item.subject || '');
      setRelationText(item.relation || '');
      setValuesText((item.values || []).map((v: any) => v.value_categorical ?? v.value_continuous).filter(Boolean).join(', '));
    }
  }, [item]);

  if (!isOpen || !item) return null;

  const handleSave = () => {
    onSave({
      source_text: sourceText,
      domain,
      visibility,
    });
  };

  return (
    <div className="edit-modal-overlay">
      <div className="edit-modal-content">
        <div className="edit-modal-header">
          <h2 className="edit-modal-title">Edit Knowledge Item</h2>
          <button
            onClick={onClose}
            className="edit-modal-close"
            disabled={isLoading}
          >
            ×
          </button>
        </div>

        <div className="edit-modal-body">
          {item.type === 'rule' ? (
            <>
              <div className="edit-modal-field">
                <label className="edit-modal-label">Conditions</label>
                <textarea
                  className="edit-modal-textarea"
                  value={conditionText}
                  onChange={(e) => setConditionText(e.target.value)}
                  rows={4}
                  disabled={isLoading}
                />
              </div>

              <div className="edit-modal-field">
                <label className="edit-modal-label">Actions</label>
                <textarea
                  className="edit-modal-textarea"
                  value={actionText}
                  onChange={(e) => setActionText(e.target.value)}
                  rows={4}
                  disabled={isLoading}
                />
              </div>
            </>
          ) : (
            <>
              <div className="edit-modal-field">
                <label className="edit-modal-label">Subject</label>
                <input
                  className="edit-modal-textarea"
                  value={subjectText}
                  onChange={(e) => setSubjectText(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="edit-modal-field">
                <label className="edit-modal-label">Relation</label>
                <input
                  className="edit-modal-textarea"
                  value={relationText}
                  onChange={(e) => setRelationText(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="edit-modal-field">
                <label className="edit-modal-label">Values</label>
                <input
                  className="edit-modal-textarea"
                  value={valuesText}
                  onChange={(e) => setValuesText(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </>
          )}

          <div className="edit-modal-field">
            <label className="edit-modal-label">Domain</label>
            <select
              className="edit-modal-select"
              value={domain || ''}
              onChange={(e) => setDomain((e.target.value as Domain) || null)}
              disabled={isLoading}
            >
              <option value="">-- Select Domain --</option>
              {DOMAINS.map((d) => (
                <option key={d} value={d}>
                  {DOMAIN_LABELS[d]}
                </option>
              ))}
            </select>
          </div>

          <div className="edit-modal-field">
            <label className="edit-modal-label">Visibility</label>
            <div className="edit-modal-radio-group">
              <label className="edit-modal-radio">
                <input
                  type="radio"
                  name="visibility"
                  value="public"
                  checked={visibility === 'public'}
                  onChange={(e) => setVisibility(e.target.value as 'public' | 'private')}
                  disabled={isLoading}
                />
                <span>Public</span>
              </label>
              <label className="edit-modal-radio">
                <input
                  type="radio"
                  name="visibility"
                  value="private"
                  checked={visibility === 'private'}
                  onChange={(e) => setVisibility(e.target.value as 'public' | 'private')}
                  disabled={isLoading}
                />
                <span>Private</span>
              </label>
            </div>
          </div>
        </div>

        <div className="edit-modal-footer">
          <button
            onClick={onClose}
            className="edit-modal-btn edit-modal-btn-secondary"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="edit-modal-btn edit-modal-btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditModal;
