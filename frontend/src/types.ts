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
