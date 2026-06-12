import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../api/AuthContext';
import { documentAPI } from '../services/api';
import type { UploadResponse, Visibility } from '../types/index';
import './Upload.css';

export const Upload: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

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
      const result = await documentAPI.upload(file, visibility);
      setResponse(result.data);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.errors?.file?.[0] ||
        'Erreur lors du téléchargement. Veuillez réessayer.'
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

  return (
    <div className="upload-container">
      {/* Header */}
      <div className="upload-header">
        <div className="upload-header-content">
          <h1>Upload Document</h1>
          <p>Traitement NLP - Desa Punggul</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="upload-main">
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
              <p className="upload-label">Sélectionnez un fichier PDF, CSV ou Excel</p>
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
                <p className="upload-visibility-label">Visibilité</p>
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
                    <span>Privé</span>
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
                  {loading ? 'Traitement...' : 'Upload'}
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
                  Annuler
                </button>
              </div>
            </>
          )}

          {error && (
            <div className="upload-error">
              <p><strong>Erreur</strong></p>
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
                <h3>Journal de traitement</h3>
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
                <p className="upload-detail-label">Type de fichier</p>
                <p className="upload-detail-value">{response.file_type.replace(/_/g, ' ').toUpperCase()}</p>
              </div>
              <div className="upload-detail-item">
                <p className="upload-detail-label">Pages</p>
                <p className="upload-detail-value">{response.pages}</p>
              </div>
              {response.text_preview && (
                <div className="upload-detail-item upload-detail-full">
                  <p className="upload-detail-label">Aperçu du texte</p>
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
              Uploader un autre document
            </button>
          </div>
        )}
      </div>

      {/* Back to Dashboard */}
      <button
        onClick={() => navigate('/dashboard')}
        className="upload-back-btn"
      >
        Retour au Dashboard
      </button>
    </div>
  );
};
