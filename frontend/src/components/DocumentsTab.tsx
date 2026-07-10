import React, { useRef } from 'react';
import { UploadCloud, FileText, Trash2, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { format } from 'date-fns';
import type { Document } from '../types';

interface DocumentsTabProps {
  documents: Document[];
  isUploading: boolean;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onDeleteDocument: (id: number) => void;
}

export function DocumentsTab({ documents, isUploading, onFileUpload, onDeleteDocument }: DocumentsTabProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const renderStatus = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'indexed': 
        return <span className="status-badge status-completed"><CheckCircle2 size={12}/> Ready</span>;
      case 'processing': return <span className="status-badge status-processing"><Clock size={12}/> Indexing...</span>;
      case 'error': return <span className="status-badge status-error"><AlertCircle size={12}/> Failed</span>;
      default: return <span className="status-badge"><Clock size={12}/> {status}</span>;
    }
  };

  return (
    <>
      <h3 className="section-title">Upload Document</h3>
      <div 
        className="upload-zone"
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud size={48} className="upload-icon" />
        <div>
          <div style={{ fontSize: '1.125rem', fontWeight: 500, marginBottom: '0.5rem' }}>
            Click to upload a document
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Supports PDF, TXT, DOCX, MD, CSV, Excel (Max 10MB)
          </div>
        </div>
        {isUploading && <div style={{ color: 'var(--accent-color)' }}>Uploading...</div>}
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={onFileUpload}
          accept=".pdf,.txt,.md,.docx,.csv,.xlsx,.xls"
        />
      </div>

      <h3 className="section-title" style={{ marginTop: '3rem' }}>Documents ({documents.length})</h3>
      {documents.length > 0 ? (
        <div className="document-grid">
          {documents.map(doc => (
            <div key={doc.id} className="document-card glass-panel">
              <div className="doc-header">
                <div className="doc-icon"><FileText size={24} /></div>
                <div className="doc-info">
                  <div className="doc-filename" title={doc.filename}>{doc.filename}</div>
                  <div className="doc-date">{format(new Date(doc.created_at), 'MMM d, h:mm a')}</div>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {renderStatus(doc.status)}
                <button 
                  className="btn btn-icon btn-danger" 
                  onClick={() => onDeleteDocument(doc.id)}
                  style={{ padding: '0.25rem', border: 'none', background: 'transparent' }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
              {doc.error_message && (
                <div style={{ fontSize: '0.75rem', color: 'var(--danger-color)', marginTop: '0.5rem' }}>
                  {doc.error_message}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          No documents uploaded yet.
        </div>
      )}
    </>
  );
}
