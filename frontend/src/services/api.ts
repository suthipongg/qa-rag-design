import type { Collection, Document } from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  // Collections
  getCollections: async (): Promise<Collection[]> => {
    const res = await fetch(`${API_BASE}/collections`);
    if (!res.ok) throw new Error('Failed to fetch collections');
    const data = await res.json();
    return data.collections;
  },

  createCollection: async (name: string, description?: string): Promise<Collection> => {
    const res = await fetch(`${API_BASE}/collections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: description || null })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || 'Failed to create collection');
    }
    return res.json();
  },

  deleteCollection: async (id: number): Promise<void> => {
    const res = await fetch(`${API_BASE}/collections/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete collection');
  },

  // Documents
  getDocuments: async (collectionId: number): Promise<Document[]> => {
    const res = await fetch(`${API_BASE}/collections/${collectionId}/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    const data = await res.json();
    return data.documents;
  },

  uploadDocument: async (collectionId: number, file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('files', file);

    const res = await fetch(`${API_BASE}/collections/${collectionId}/documents`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => null);
      throw new Error(errorData?.detail || 'Failed to upload document');
    }
    const data = await res.json();
    return data[0];
  },

  deleteDocument: async (documentId: number): Promise<void> => {
    const res = await fetch(`${API_BASE}/documents/${documentId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  retrieveChunks: async (collectionId: number, query: string, topK: number = 5): Promise<any[]> => {
    const res = await fetch(`${API_BASE}/collections/${collectionId}/retrieve?query=${encodeURIComponent(query)}&top_k=${topK}`);
    if (!res.ok) throw new Error('Failed to retrieve chunks');
    return res.json();
  },

  askQuestion: async (collectionId: number, question: string, conversationId?: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/collections/${collectionId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, conversation_id: conversationId || null })
    });
    if (!res.ok) throw new Error('Failed to generate answer');
    return res.json();
  },

  getChatHistory: async (collectionId: number, conversationId: string): Promise<any[]> => {
    const res = await fetch(`${API_BASE}/collections/${collectionId}/chat/conversations/${conversationId}`);
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
  }
};

