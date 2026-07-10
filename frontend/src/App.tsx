import React, { useState, useEffect, useRef } from 'react';
import { api } from './services/api';
import type { Collection, Document } from './types';
import { 
  FolderPlus, 
  Trash2, 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  BookOpen,
  Plus
} from 'lucide-react';
import { format } from 'date-fns';

function App() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [activeCollection, setActiveCollection] = useState<Collection | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newColName, setNewColName] = useState('');
  const [newColDesc, setNewColDesc] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load collections on mount
  useEffect(() => {
    fetchCollections();
  }, []);

  // Load documents when active collection changes
  useEffect(() => {
    if (activeCollection) {
      fetchDocuments(activeCollection.id);
      
      // Auto-refresh documents every 5 seconds to get processing status
      const interval = setInterval(() => fetchDocuments(activeCollection.id), 5000);
      return () => clearInterval(interval);
    } else {
      setDocuments([]);
    }
  }, [activeCollection]);

  const fetchCollections = async () => {
    try {
      const data = await api.getCollections();
      setCollections(data);
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  const fetchDocuments = async (collectionId: number) => {
    try {
      const data = await api.getDocuments(collectionId);
      setDocuments(data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleCreateCollection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColName.trim()) return;
    try {
      const newCol = await api.createCollection(newColName, newColDesc);
      setCollections([...collections, newCol]);
      setIsModalOpen(false);
      setNewColName('');
      setNewColDesc('');
      setActiveCollection(newCol);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Error creating collection');
    }
  };

  const handleDeleteCollection = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this collection and all its documents?')) return;
    try {
      await api.deleteCollection(id);
      setCollections(collections.filter(c => c.id !== id));
      if (activeCollection?.id === id) setActiveCollection(null);
    } catch (error) {
      console.error('Error deleting collection:', error);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !activeCollection) return;
    
    setIsUploading(true);
    try {
      await api.uploadDocument(activeCollection.id, file);
      await fetchDocuments(activeCollection.id);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDeleteDocument = async (id: number) => {
    if (!confirm('Delete this document?')) return;
    try {
      await api.deleteDocument(id);
      setDocuments(documents.filter(d => d.id !== id));
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

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
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar glass-panel">
        <h2 className="title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <BookOpen size={24} /> Knowledge
        </h2>
        
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)} style={{ width: '100%' }}>
          <Plus size={18} /> New Collection
        </button>

        <div className="collection-list">
          {collections.map(col => (
            <div 
              key={col.id} 
              className={`collection-item ${activeCollection?.id === col.id ? 'active' : ''}`}
              onClick={() => setActiveCollection(col)}
            >
              <div>
                <div className="collection-name">{col.name}</div>
                <div className="collection-meta">
                  {format(new Date(col.created_at), 'MMM d, yyyy')}
                </div>
              </div>
              <button 
                className="btn btn-icon btn-danger" 
                onClick={(e) => handleDeleteCollection(col.id, e)}
                style={{ padding: '0.25rem', border: 'none', background: 'transparent' }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content glass-panel">
        {activeCollection ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
              <div>
                <h1 className="title" style={{ marginBottom: '0.5rem' }}>{activeCollection.name}</h1>
                {activeCollection.description && (
                  <p style={{ color: 'var(--text-secondary)' }}>{activeCollection.description}</p>
                )}
              </div>
            </div>

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
                onChange={handleFileUpload}
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
                        onClick={() => handleDeleteDocument(doc.id)}
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
        ) : (
          <div className="empty-state">
            <FolderPlus size={64} style={{ opacity: 0.5 }} />
            <h2 style={{ fontSize: '1.5rem', fontWeight: 500 }}>No Collection Selected</h2>
            <p>Select a collection from the sidebar or create a new one to manage documents.</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
            <h2 className="title" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Create Collection</h2>
            <form onSubmit={handleCreateCollection}>
              <div className="input-group">
                <label className="input-label">Name</label>
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="e.g., HR Policies" 
                  value={newColName}
                  onChange={e => setNewColName(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="input-group">
                <label className="input-label">Description (Optional)</label>
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="Brief description..." 
                  value={newColDesc}
                  onChange={e => setNewColDesc(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button type="button" className="btn" onClick={() => setIsModalOpen(false)} style={{ flex: 1 }}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={!newColName.trim()}>Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
