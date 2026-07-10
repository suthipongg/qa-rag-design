import React, { useState } from 'react';
import { Sliders } from 'lucide-react';
import type { Citation } from '../types';

interface RetrievalPlaygroundTabProps {
  onRetrieve: (query: string, topK: number) => Promise<void>;
  retrievedChunks: Citation[];
  isSearching: boolean;
}

export function RetrievalPlaygroundTab({ onRetrieve, retrievedChunks, isSearching }: RetrievalPlaygroundTabProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [topK, setTopK] = useState(5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onRetrieve(searchQuery, topK);
    }
  };

  const getScoreClass = (score: number) => {
    if (score >= 0.7) return 'high';
    if (score >= 0.5) return 'med';
    return '';
  };

  return (
    <div>
      <h3 className="section-title">Query Retrieval Tester</h3>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', marginBottom: '2.5rem' }}>
        <div style={{ flex: 1 }} className="input-group">
          <label className="input-label">Type search query</label>
          <input 
            type="text"
            className="input-field"
            placeholder="e.g. What is the cancellation fee?"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
        <div style={{ width: '120px' }} className="input-group">
          <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Sliders size={14} /> Top K</label>
          <input 
            type="number"
            className="input-field"
            value={topK}
            min={1}
            max={20}
            onChange={e => setTopK(parseInt(e.target.value) || 5)}
          />
        </div>
        <button type="submit" className="btn btn-primary" style={{ height: '42px' }} disabled={!searchQuery.trim() || isSearching}>
          {isSearching ? 'Searching...' : 'Retrieve'}
        </button>
      </form>

      <h3 className="section-title">Match Results ({retrievedChunks.length})</h3>
      <div className="playground-results">
        {retrievedChunks.length > 0 ? (
          retrievedChunks.map((chunk, i) => (
            <div key={i} className="chunk-card">
              <div className="chunk-header">
                <div className="chunk-meta">
                  <span style={{ fontWeight: 'bold', color: 'var(--accent-color)' }}>#{i+1}</span>
                  <span>📄 {chunk.document_name}</span>
                  {chunk.page_number && <span>Page: {chunk.page_number}</span>}
                  {chunk.row_range && <span>Rows: {chunk.row_range}</span>}
                </div>
                <div className={`chunk-score ${getScoreClass(chunk.relevance_score)}`}>
                  Score: {chunk.relevance_score.toFixed(4)}
                </div>
              </div>
              <div className="chunk-text">{chunk.chunk_text}</div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            No search results yet. Type a query above to fetch chunks.
          </div>
        )}
      </div>
    </div>
  );
}
