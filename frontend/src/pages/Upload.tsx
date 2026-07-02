import React, { useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { documentAPI } from '../services/api';
import type { UploadResponse, Visibility } from '../types/index';
import './Upload.css';

export const Upload: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [file, setFile] = useState<File | null>(null);
  const [visibility, setVisibility] = useState<Visibility>('private');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Redirect if not admin
  React.useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/');
    }
  }, [user, navigate]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      const validTypes = ['application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
      
      if (validTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Format invalide. Veuillez uploader PDF, CSV, ou Excel.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      // Log token and user info
      const token = localStorage.getItem('token');
      console.log('Upload attempt:', {
        token: token ? 'Present' : 'Missing',
        tokenLength: token?.length,
        user: user?.username,
        userRole: user?.role,
        file: file.name,
        visibility
      });

      const result = await documentAPI.upload(file, visibility);
      console.log('Upload success:', result.data);
      setResponse(result.data);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      console.error('Upload error:', {
        status: err.response?.status,
        message: err.response?.data?.message,
        fullError: err.response?.data
      });
      setError(
        err.response?.data?.message ||
        err.response?.data?.errors?.file?.[0] ||
        'Error during upload. Please try again.'
      );
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const getAlertStyles = (routing: string) => {
    switch (routing) {
      case 'rejected':
        return { bg: 'bg-red-100', border: 'border-red-300', text: 'text-red-800' };
      case 'pipeline1':
        return { bg: 'bg-green-100', border: 'border-green-300', text: 'text-green-800' };
      case 'pipeline2_direct':
        return { bg: 'bg-blue-100', border: 'border-blue-300', text: 'text-blue-800' };
      case 'ocr_then_pipeline1':
        return { bg: 'bg-orange-100', border: 'border-orange-300', text: 'text-orange-800' };
      default:
        return { bg: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-800' };
    }
  };

  const getAlertMessage = (routing: string) => {
    switch (routing) {
      case 'rejected':
        return 'Document rejeté — contenu insuffisant';
      case 'pipeline1':
        return 'Document routé vers Pipeline 1 — Extraction de connaissances';
      case 'pipeline2_direct':
        return 'Données structurées détectées — routé vers Pipeline 2';
      case 'ocr_then_pipeline1':
        return 'PDF scanné détecté — OCR appliqué, routé vers Pipeline 1';
      default:
        return 'Document traité';
    }
  };

  const alertStyles = response ? getAlertStyles(response.routing) : null;

  const isActive = (path: string) => location.pathname === path ? 'active' : '';

  return (
    <div className="upload-container">
      {/* Sidebar Navigation */}
      <div className="upload-sidebar">
        <div className="upload-sidebar-title">
          <h3>Menu</h3>
        </div>
        <ul className="upload-sidebar-menu">
          <li className="upload-sidebar-item">
            <a href="/dashboard" className={`upload-sidebar-link ${isActive('/dashboard')}`}>
              Dashboard
            </a>
          </li>
          <li className="upload-sidebar-item">
            <a href="/rules" className={`upload-sidebar-link ${isActive('/rules')}`}>
              Knowledge Rules
            </a>
          </li>
          <li className="upload-sidebar-item">
            <a href="/facts" className={`upload-sidebar-link ${isActive('/facts')}`}>
              Knowledge Facts
            </a>
          </li>
          {user?.role === 'admin' && (
            <>
              <li className="upload-sidebar-item">
                <a href="/pending-review" className={`upload-sidebar-link ${isActive('/pending-review')}`}>
                  Pending Review
                </a>
              </li>
              <li className="upload-sidebar-item">
                <a href="/upload" className={`upload-sidebar-link ${isActive('/upload')}`}>
                  Upload
                </a>
              </li>
            </>
          )}
        </ul>
      </div>

      {/* Main Content */}
      <div className="upload-main">
        {/* Header */}
        <div className="upload-header">
          <div className="upload-header-content">
            <h1>Upload Document</h1>
            <p>NLP Processing - Desa Punggul</p>
          </div>
        </div>

        {/* Content */}
        <div className="upload-main-content">
          <div className="upload-card">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.csv,.xlsx,.xls"
            onChange={handleFileSelect}
            className="hidden"
            disabled={loading}
          />

          {!file && !response && (
            <>
              <p className="upload-label">Select a PDF, CSV or Excel file</p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="upload-btn"
                disabled={loading}
              >
                Select File
              </button>
            </>
          )}

          {file && !response && (
            <>
              <p className="upload-file-selected">{file.name}</p>
              
              <div className="upload-visibility">
                <p className="upload-visibility-label">Visibility</p>
                <div className="upload-visibility-options">
                  <label className="upload-radio-label">
                    <input
                      type="radio"
                      name="visibility"
                      value="private"
                      checked={visibility === 'private'}
                      onChange={(e) => setVisibility(e.target.value as Visibility)}
                      disabled={loading}
                    />
                    <span>Private</span>
                  </label>
                  <label className="upload-radio-label">
                    <input
                      type="radio"
                      name="visibility"
                      value="public"
                      checked={visibility === 'public'}
                      onChange={(e) => setVisibility(e.target.value as Visibility)}
                      disabled={loading}
                    />
                    <span>Public</span>
                  </label>
                </div>
              </div>

              <div className="upload-actions">
                <button
                  onClick={handleUpload}
                  disabled={loading}
                  className="upload-btn"
                >
                  {loading ? 'Processing...' : 'Upload'}
                </button>
                <button
                  onClick={() => {
                    setFile(null);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                    setError(null);
                  }}
                  className="upload-btn-secondary"
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </>
          )}

          {error && (
            <div className="upload-error">
              <p><strong>Error</strong></p>
              <p>{error}</p>
            </div>
          )}
        </div>

        {response && (
          <div className="upload-results">
            
            {/* Alert */}
            {alertStyles && (
              <div className={`upload-alert upload-alert-${response.routing}`}>
                <p>{getAlertMessage(response.routing)}</p>
              </div>
            )}

            {/* Log */}
            <div className="upload-log">
              <div className="upload-log-header">
                <h3>Processing Log</h3>
              </div>
              <div className="upload-log-content">
                {response.log.map((logEntry, index) => (
                  <div key={index} className="upload-log-entry">
                    {logEntry}
                  </div>
                ))}
              </div>
            </div>

            {/* Details */}
            <div className="upload-details">
              <div className="upload-detail-item">
                <p className="upload-detail-label">File Type</p>
                <p className="upload-detail-value">{response.file_type.replace(/_/g, ' ').toUpperCase()}</p>
              </div>
              <div className="upload-detail-item">
                <p className="upload-detail-label">Pages</p>
                <p className="upload-detail-value">{response.pages}</p>
              </div>
              {response.text_preview && (
                <div className="upload-detail-item upload-detail-full">
                  <p className="upload-detail-label">Text Preview</p>
                  <p className="upload-detail-preview">{response.text_preview}</p>
                </div>
              )}
            </div>

            {/* Back Button */}
            <button
              onClick={() => {
                setFile(null);
                setResponse(null);
                setError(null);
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
              className="upload-btn upload-btn-full"
            >
              Upload Another Document
            </button>
          </div>
        )}
        </div>
      </div>
    </div>
  );
};
