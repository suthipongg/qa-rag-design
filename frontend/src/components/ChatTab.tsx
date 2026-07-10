import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, AlertTriangle } from 'lucide-react';
import type { ChatMessage } from '../types';

interface ChatTabProps {
  chatHistory: ChatMessage[];
  isChatSending: boolean;
  onChatSubmit: (query: string) => Promise<void>;
}

export function ChatTab({ chatHistory, isChatSending, onChatSubmit }: ChatTabProps) {
  const [chatQuery, setChatQuery] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim() || isChatSending) return;
    const q = chatQuery;
    setChatQuery('');
    await onChatSubmit(q);
  };

  return (
    <div className="chat-container">
      <div className="chat-history">
        {chatHistory.length > 0 ? (
          chatHistory.map((msg, i) => (
            <div key={i} className={`chat-message-bubble ${msg.role} fade-in`}>
              {/* If there's a rewritten query and it's a user message */}
              {msg.role === 'user' && msg.rewritten_question && (
                <div className="rewritten-question-info">
                  🔍 Standalone Query: "{msg.rewritten_question}"
                </div>
              )}
              
              {/* If it's an assistant message without sufficient evidence */}
              {msg.role === 'assistant' && msg.has_sufficient_evidence === false && (
                <div className="insufficient-evidence-alert">
                  <AlertTriangle size={16} /> 
                  Could not find sufficient evidence in the documents.
                </div>
              )}

              <div className="message-content">
                {msg.content}
              </div>

              {/* Citations for assistant messages */}
              {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                <div className="citations-container">
                  <div className="citations-label">Sources:</div>
                  <div className="citations-list">
                    {msg.citations.map((cite, idx) => (
                      <div key={idx} className="citation-badge" title={cite.chunk_text}>
                        <span className="citation-number">[{idx + 1}]</span>
                        <span className="citation-doc">{cite.document_name}</span>
                        {cite.page_number && <span className="citation-page">p.{cite.page_number}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)', gap: '0.5rem' }}>
            <MessageSquare size={36} style={{ opacity: 0.4 }} />
            <div>Start a conversational QA session about this collection.</div>
          </div>
        )}
        {isChatSending && (
          <div className="chat-message-bubble assistant fade-in" style={{ fontStyle: 'italic', opacity: 0.7 }}>
            <span className="typing-indicator">AI is synthesizing answer...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-bar">
        <input 
          type="text"
          className="input-field"
          placeholder="Ask a question about the uploaded documents..."
          value={chatQuery}
          onChange={e => setChatQuery(e.target.value)}
          style={{ flex: 1 }}
          disabled={isChatSending}
        />
        <button type="submit" className="btn btn-primary" disabled={!chatQuery.trim() || isChatSending}>
          <Send size={16} /> Send
        </button>
      </form>
    </div>
  );
}
