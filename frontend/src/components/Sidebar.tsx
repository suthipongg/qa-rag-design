import React, { useState } from 'react';
import { BookOpen, Plus, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import type { Collection } from '../types';

interface SidebarProps {
  collections: Collection[];
  activeCollection: Collection | null;
  onSelectCollection: (col: Collection) => void;
  onCreateCollection: (name: string, description: string) => Promise<void>;
  onDeleteCollection: (id: number, e: React.MouseEvent) => void;
}

export function Sidebar({ collections, activeCollection, onSelectCollection, onCreateCollection, onDeleteCollection }: SidebarProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newColName, setNewColName] = useState('');
  const [newColDesc, setNewColDesc] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColName.trim()) return;
    await onCreateCollection(newColName, newColDesc);
    setIsModalOpen(false);
    setNewColName('');
    setNewColDesc('');
  };

  return (
    <>
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
              onClick={() => onSelectCollection(col)}
            >
              <div>
                <div className="collection-name">{col.name}</div>
                <div className="collection-meta">
                  {format(new Date(col.created_at), 'MMM d, yyyy')}
                </div>
              </div>
              <button 
                className="btn btn-icon btn-danger" 
                onClick={(e) => onDeleteCollection(col.id, e)}
                style={{ padding: '0.25rem', border: 'none', background: 'transparent' }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
            <h2 className="title" style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Create Collection</h2>
            <form onSubmit={handleCreate}>
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
    </>
  );
}
