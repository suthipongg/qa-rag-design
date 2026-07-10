import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import type { Collection, Document, Citation, ChatMessage } from './types';
import { FolderPlus, FileText, Search, MessageSquare } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { DocumentsTab } from './components/DocumentsTab';
import { RetrievalPlaygroundTab } from './components/RetrievalPlaygroundTab';
import { ChatTab } from './components/ChatTab';

function App() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [activeCollection, setActiveCollection] = useState<Collection | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const [activeTab, setActiveTab] = useState<'documents' | 'retrieval' | 'chat'>('documents');

  const [retrievedChunks, setRetrievedChunks] = useState<Citation[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isChatSending, setIsChatSending] = useState(false);

  useEffect(() => {
    fetchCollections();
  }, []);

  useEffect(() => {
    if (activeCollection) {
      fetchDocuments(activeCollection.id);
      const interval = setInterval(() => fetchDocuments(activeCollection.id), 5000);
      return () => clearInterval(interval);
    } else {
      setDocuments([]);
    }
  }, [activeCollection]);

  useEffect(() => {
    setActiveTab('documents');
    setRetrievedChunks([]);
    setChatHistory([]);
    setConversationId(null);
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

  const handleCreateCollection = async (name: string, desc: string) => {
    try {
      const newCol = await api.createCollection(name, desc);
      setCollections([...collections, newCol]);
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
      e.target.value = '';
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

  const handleRetrieveTest = async (query: string, topK: number) => {
    if (!activeCollection || !query.trim()) return;
    setIsSearching(true);
    try {
      const chunks = await api.retrieveChunks(activeCollection.id, query, topK);
      setRetrievedChunks(chunks);
    } catch (error) {
      alert('Error searching chunks');
      console.error(error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleChatSubmit = async (query: string) => {
    if (!activeCollection || !query.trim() || isChatSending) return;

    const userMsg: ChatMessage = { role: 'user', content: query };
    setChatHistory(prev => [...prev, userMsg]);
    setIsChatSending(true);

    try {
      const res = await api.askQuestion(activeCollection.id, query, conversationId || undefined);
      if (!conversationId) {
        setConversationId(res.conversation_id);
      }
      
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.answer,
        rewritten_question: res.rewritten_question || undefined,
        citations: res.citations,
        has_sufficient_evidence: res.has_sufficient_evidence
      };
      
      setChatHistory(prev => {
        const newHistory = [...prev];
        const lastUserIdx = newHistory.length - 1;
        if (newHistory[lastUserIdx].role === 'user' && res.rewritten_question) {
           newHistory[lastUserIdx] = { ...newHistory[lastUserIdx], rewritten_question: res.rewritten_question };
        }
        return [...newHistory, assistantMsg];
      });

    } catch (error) {
      const errMsg: ChatMessage = {
        role: 'assistant',
        content: 'Error: Failed to get answer from server.'
      };
      setChatHistory(prev => [...prev, errMsg]);
      console.error(error);
    } finally {
      setIsChatSending(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        collections={collections}
        activeCollection={activeCollection}
        onSelectCollection={setActiveCollection}
        onCreateCollection={handleCreateCollection}
        onDeleteCollection={handleDeleteCollection}
      />

      <div className="main-content glass-panel">
        {activeCollection ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
              <div>
                <h1 className="title" style={{ marginBottom: '0.25rem' }}>{activeCollection.name}</h1>
                {activeCollection.description && (
                  <p style={{ color: 'var(--text-secondary)' }}>{activeCollection.description}</p>
                )}
              </div>
            </div>

            <div className="tab-container">
              <button 
                className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
                onClick={() => setActiveTab('documents')}
                style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <FileText size={16} /> Documents
              </button>
              <button 
                className={`tab-btn ${activeTab === 'retrieval' ? 'active' : ''}`}
                onClick={() => setActiveTab('retrieval')}
                style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <Search size={16} /> Retrieval Playground
              </button>
              <button 
                className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat')}
                style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <MessageSquare size={16} /> Chat Q&A
              </button>
            </div>

            {activeTab === 'documents' && (
              <DocumentsTab 
                documents={documents}
                isUploading={isUploading}
                onFileUpload={handleFileUpload}
                onDeleteDocument={handleDeleteDocument}
              />
            )}

            {activeTab === 'retrieval' && (
              <RetrievalPlaygroundTab 
                onRetrieve={handleRetrieveTest}
                retrievedChunks={retrievedChunks}
                isSearching={isSearching}
              />
            )}

            {activeTab === 'chat' && (
              <ChatTab 
                chatHistory={chatHistory}
                isChatSending={isChatSending}
                onChatSubmit={handleChatSubmit}
              />
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
    </div>
  );
}

export default App;
