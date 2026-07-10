export interface Collection {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface Document {
  id: number;
  collection_id: number;
  filename: string;
  file_hash: string;
  status: string; // 'pending', 'processing', 'completed', 'error'
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document_id: number;
  document_name: string;
  chunk_text: string;
  page_number?: number;
  row_range?: string;
  relevance_score: number;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  rewritten_question?: string;
  citations?: Citation[];
  has_sufficient_evidence?: boolean;
  created_at?: string;
}
