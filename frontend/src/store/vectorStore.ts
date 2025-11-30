import { create } from 'zustand';
import { vectorsApi } from '../api/vectors';
import type { VectorCollection, SearchResponse } from '../api/vectors';

interface VectorState {
  collections: VectorCollection[];
  currentCollection: VectorCollection | null;
  searchResults: SearchResponse | null;
  isLoading: boolean;

  fetchCollections: () => Promise<void>;
  fetchCollectionDetails: (name: string) => Promise<void>;
  createCollection: (name: string, documents: any[]) => Promise<VectorCollection>;
  deleteCollection: (name: string) => Promise<void>;
  setCurrentCollection: (collection: VectorCollection | null) => void;
  search: (collectionName: string, query: string, topK?: number) => Promise<SearchResponse>;
  clearSearchResults: () => void;
}

export const useVectorStore = create<VectorState>((set, get) => ({
  collections: [],
  currentCollection: null,
  searchResults: null,
  isLoading: false,

  fetchCollections: async () => {
    set({ isLoading: true });
    try {
      const collections = await vectorsApi.list();
      set({ collections, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchCollectionDetails: async (name: string) => {
    set({ isLoading: true });
    try {
      const collection = await vectorsApi.get(name);
      set({ currentCollection: collection, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createCollection: async (name: string, documents: any[]) => {
    const collection = await vectorsApi.create({ name, documents });
    set({ collections: [...get().collections, collection] });
    return collection;
  },

  deleteCollection: async (name: string) => {
    await vectorsApi.delete(name);
    set({
      collections: get().collections.filter((c) => c.name !== name),
      currentCollection: get().currentCollection?.name === name ? null : get().currentCollection,
    });
  },

  setCurrentCollection: (collection: VectorCollection | null) => {
    set({ currentCollection: collection });
  },

  search: async (collectionName: string, query: string, topK = 5) => {
    try {
      const results = await vectorsApi.search(collectionName, { query, top_k: topK });
      set({ searchResults: results });
      return results;
    } catch (error) {
      set({ searchResults: null });
      throw error;
    }
  },

  clearSearchResults: () => {
    set({ searchResults: null });
  },
}));

