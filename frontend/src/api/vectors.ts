import client from './client';

export interface DocumentInput {
  text: string;
  metadata?: Record<string, any>;
}

export interface VectorCollection {
  id: string;
  user_id: string;
  name: string;
  dimension: number;
  document_count: number;
  created_at: string;
}

export interface CreateCollectionRequest {
  name: string;
  documents: DocumentInput[];
}

export interface AddDocumentsRequest {
  documents: DocumentInput[];
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  score_threshold?: number;
  metadata_filter?: Record<string, any>;
}

export interface SearchResult {
  text: string;
  score: number;
  metadata: Record<string, any>;
}

export interface SearchResponse {
  query: string;
  collection_name: string;
  results: SearchResult[];
  total_results: number;
  top_k: number;
  score_threshold?: number;
}

export const vectorsApi = {
  list: async (): Promise<VectorCollection[]> => {
    const response = await client.get('/vectors/collections');
    return response.data;
  },

  create: async (data: CreateCollectionRequest): Promise<VectorCollection> => {
    const response = await client.post('/vectors/collections', data);
    return response.data;
  },

  get: async (name: string): Promise<VectorCollection> => {
    const response = await client.get(`/vectors/collections/${name}`);
    return response.data;
  },

  addDocuments: async (name: string, data: AddDocumentsRequest): Promise<any> => {
    const response = await client.post(`/vectors/collections/${name}/documents`, data);
    return response.data;
  },

  uploadFiles: async (
    name: string,
    files: File[],
    metadata?: Record<string, any>,
    chunkSize: number = 1000,
    chunkOverlap: number = 200
  ): Promise<any> => {
    const formData = new FormData();
    
    // Add files
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    // Add metadata if provided
    if (metadata && Object.keys(metadata).length > 0) {
      formData.append('metadata_json', JSON.stringify(metadata));
    }
    
    // Add chunk settings
    formData.append('chunk_size', chunkSize.toString());
    formData.append('chunk_overlap', chunkOverlap.toString());
    
    const response = await client.post(`/vectors/collections/${name}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  search: async (name: string, data: SearchRequest): Promise<SearchResponse> => {
    const response = await client.post(`/vectors/collections/${name}/search`, data);
    return response.data;
  },

  delete: async (name: string): Promise<void> => {
    await client.delete(`/vectors/collections/${name}`);
  },
};

