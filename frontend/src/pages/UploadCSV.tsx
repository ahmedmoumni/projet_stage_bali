import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Papa from 'papaparse';
import { useAuth } from '../api/AuthContext';
import { pipeline3API } from '../services/api';
import type { CSVColumn, DiscoverResponse } from '../types';
import './Upload.css';
import './UploadCSV.css';

export const UploadCSV: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [file, setFile] = useState<File | null>(null);
  const [rawRows, setRawRows] = useState<string[][]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [columns, setColumns] = useState<CSVColumn[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<DiscoverResponse | null>(null);

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const isActive = (path: string) => (location.pathname === path ? 'active' : '');

  const handleFileSelection = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a CSV file.');
      return;
    }

    setFile(selectedFile);
    setResponse(null);
    setError(null);

    Papa.parse<string[]>(selectedFile, {
      header: false,
      skipEmptyLines: true,
      complete: (result) => {
        const parsedRows = result.data as string[][];
        if (parsedRows.length === 0) {
          setHeaders([]);
          setColumns([]);
          setRawRows([]);
          return;
        }

        const parsedHeaders = parsedRows[0].map((header) => header.trim());
        const previewRows = parsedRows.slice(1, 6);

        setHeaders(parsedHeaders);
        setRawRows(previewRows);
        setColumns(
          parsedHeaders.map((header, index) => ({
            name: header,
            role: 'ignore',
            samples: previewRows
              .map((row) => row[index] ?? '')
              .filter((value) => value !== '')
              .slice(0, 3),
          }))
        );
      },
      error: () => {
        setError('Unable to read the selected CSV file.');
      },
    });
  };

  const updateColumnRole = (columnName: string, role: CSVColumn['role']) => {
    setColumns((current) =>
      current.map((column) => (column.name === columnName ? { ...column, role } : column))
    );
  };

  const validationError = useMemo(() => {
    const subjectColumns = columns.filter((column) => column.role === 'subject');
    const targetColumns = columns.filter((column) => column.role === 'target');
    const featureColumns = columns.filter((column) => column.role === 'feature');

    if (!file) {
      return 'Please upload a CSV file first.';
    }
    if (subjectColumns.length !== 1) {
      return 'Exactly one column must be assigned as Subject.';
    }
    if (targetColumns.length !== 1) {
      return 'Exactly one column must be assigned as Target.';
    }
    if (featureColumns.length < 1) {
      return 'At least one column must be assigned as Feature.';
    }
    return null;
  }, [columns, file]);

  const handleDiscover = async () => {
    if (!file) {
      setError('Please upload a CSV file.');
      return;
    }

    if (validationError) {
      setError(validationError);
      return;
    }

    const subjectColumn = columns.find((column) => column.role === 'subject')?.name;
    const targetColumn = columns.find((column) => column.role === 'target')?.name;
    const featureColumns = columns.filter((column) => column.role === 'feature').map((column) => column.name);

    if (!subjectColumn || !targetColumn || featureColumns.length === 0) {
      setError('Please complete the column configuration before discovering rules.');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await pipeline3API.discover(file, subjectColumn, targetColumn, featureColumns);
      setResponse(result.data);
    } catch (err: any) {
      const message = err.response?.data?.log?.[0] || err.response?.data?.message || 'Discovery failed.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
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
                <a href="/analytics" className={`upload-sidebar-link ${isActive('/analytics')}`}>
                  Analytics
                </a>
              </li>
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
              <li className="upload-sidebar-item">
                <a href="/upload-csv" className={`upload-sidebar-link ${isActive('/upload-csv')}`}>
                  Rule Discovery
                </a>
              </li>
            </>
          )}
        </ul>
      </div>

      <div className="upload-main">
        <div className="upload-main-content">
          <div className="upload-card upload-card--wide">
            <div className="upload-card-header">
              <h1>Upload CSV for Rule Discovery</h1>
              <p>Assign one Subject, one Target, and one or more Features before launching Pipeline 3.</p>
            </div>

            <label htmlFor="csv-upload" className="upload-dropzone">
              <input id="csv-upload" type="file" accept=".csv" onChange={handleFileSelection} className="upload-file-input" />
              <div>
                <strong>{file ? file.name : 'Click to upload a CSV file'}</strong>
                <div className="upload-dropzone-subtitle">CSV files only</div>
              </div>
            </label>

            {headers.length > 0 && (
              <div className="upload-section">
                <h3>Preview</h3>
                <div className="upload-table-container">
                  <table className="upload-table">
                    <thead>
                      <tr>
                        {headers.map((header) => (
                          <th key={header}>{header}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rawRows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((value, colIndex) => (
                            <td key={`${rowIndex}-${colIndex}`}>{value}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="upload-columns-grid">
                  {columns.map((column) => (
                    <div key={column.name} className="upload-column-card">
                      <div className="upload-column-card-header">
                        <strong>{column.name}</strong>
                        <select
                          value={column.role}
                          onChange={(event) => updateColumnRole(column.name, event.target.value as CSVColumn['role'])}
                          className="upload-select"
                        >
                          <option value="subject">Subject</option>
                          <option value="target">Target</option>
                          <option value="feature">Feature</option>
                          <option value="ignore">Ignore</option>
                        </select>
                      </div>
                      <div className="upload-column-samples">Samples: {column.samples.join(', ') || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <div className="upload-error">
                <p>Error</p>
                <p>{error}</p>
              </div>
            )}

            <div className="upload-actions">
              <button onClick={handleDiscover} disabled={loading} className="upload-btn">
                {loading ? 'Discovering...' : 'Discover Rules'}
              </button>
            </div>

            {response && (
              <div className="upload-results">
                <h3>Processing Log</h3>
                <ul>
                  {response.log.map((entry, index) => (
                    <li key={index}>{entry}</li>
                  ))}
                </ul>
                <div className="upload-summary">{response.rules_discovered} rules discovered and stored</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
