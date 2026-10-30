import axios from 'axios';
import {
  Job,
  PaginatedResponse,
  Profile,
  Recommendation,
  RecommendationDetail,
  Resume,
  ResumeAnalysis,
  SavedJob,
  User,
  UserPreferences,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to requests automatically
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('jobpilot_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept 401s and unauthenticated 403s
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isUnauth =
      error.response?.status === 401 ||
      (error.response?.status === 403 &&
        (error.response?.data?.detail === 'Not authenticated' ||
          error.response?.data?.detail === 'Invalid or expired token'));

    if (isUnauth) {
      localStorage.removeItem('jobpilot_token');
      localStorage.removeItem('jobpilot_user');
      if (
        typeof window !== 'undefined' &&
        !window.location.pathname.includes('/login') &&
        !window.location.pathname.includes('/register')
      ) {
        window.location.href = '/login?expired=true';
      }
    }
    return Promise.reject(error);
  }
);


export const api = {
  // ── Auth ────────────────────────────────────────────────────────────
  login: async (data: any) => {
    const res = await apiClient.post('/auth/login', data);
    return res.data;
  },
  register: async (data: any) => {
    const res = await apiClient.post('/auth/register', data);
    return res.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
  sendOTP: async (email: string) => {
    const res = await apiClient.post('/auth/send-otp', { email });
    return res.data;
  },
  verifyOTP: async (email: string, otp: string) => {
    const res = await apiClient.post('/auth/verify-otp', { email, otp });
    return res.data;
  },
  forgotPassword: async (email: string) => {
    const res = await apiClient.post('/auth/forgot-password', { email });
    return res.data;
  },
  resetPassword: async (token: string, new_password: string) => {
    const res = await apiClient.post('/auth/reset-password', { token, new_password });
    return res.data;
  },

  // ── Profile ─────────────────────────────────────────────────────────
  getProfile: async (): Promise<Profile> => {
    const res = await apiClient.get('/profile');
    return res.data;
  },
  updateProfile: async (data: Partial<Profile>): Promise<Profile> => {
    const res = await apiClient.put('/profile', data);
    return res.data;
  },
  getPreferences: async (): Promise<UserPreferences> => {
    const res = await apiClient.get('/profile/preferences');
    return res.data;
  },
  updatePreferences: async (data: Partial<UserPreferences>): Promise<UserPreferences> => {
    const res = await apiClient.put('/profile/preferences', data);
    return res.data;
  },

  // ── Resumes ─────────────────────────────────────────────────────────
  uploadResume: async (file: File): Promise<Resume> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  getResumes: async (): Promise<Resume[]> => {
    try {
      const res = await apiClient.get('/resume/list');
      if (Array.isArray(res.data)) return res.data;
      return res.data ? [res.data] : [];
    } catch {
      try {
        const res = await apiClient.get('/resume');
        return res.data ? [res.data] : [];
      } catch {
        return [];
      }
    }
  },
  getResumeAnalysis: async (resumeId?: number): Promise<ResumeAnalysis> => {
    const url = resumeId ? `/resume/${resumeId}/analysis` : '/resume/analysis';
    const res = await apiClient.get(url);
    return res.data;
  },
  getLatestAnalysis: async (): Promise<ResumeAnalysis | null> => {
    const res = await apiClient.get('/resume/analysis');
    return res.data;
  },
  analyzeResume: async (): Promise<ResumeAnalysis> => {
    const res = await apiClient.post('/resume/analyze');
    return res.data;
  },
  deleteResume: async () => {
    const res = await apiClient.delete('/resume');
    return res.data;
  },

  // ── Jobs ────────────────────────────────────────────────────────────
  getJobs: async (params?: Record<string, any>): Promise<PaginatedResponse<Job>> => {
    const res = await apiClient.get('/jobs', { params });
    return res.data;
  },
  getJobDetail: async (id: number): Promise<Job> => {
    const res = await apiClient.get(`/jobs/${id}`);
    return res.data;
  },
  getJobStats: async () => {
    const res = await apiClient.get('/jobs/stats/summary');
    return res.data;
  },
  syncJobs: async (maxPerSource: number = 30) => {
    const res = await apiClient.post('/jobs/sync', null, {
      params: { max_per_source: maxPerSource },
    });
    return res.data;
  },
  saveJob: async (jobId: number, status: string = 'saved', notes?: string): Promise<SavedJob> => {
    const res = await apiClient.post(`/jobs/${jobId}/save`, { status, notes });
    return res.data;
  },
  unsaveJob: async (jobId: number) => {
    const res = await apiClient.delete(`/jobs/${jobId}/save`);
    return res.data;
  },
  getSavedJobs: async (): Promise<SavedJob[]> => {
    const res = await apiClient.get('/jobs/saved');
    return res.data;
  },
  trackInteraction: async (jobId: number, type: string) => {
    const res = await apiClient.post(`/jobs/${jobId}/interact`, {
      interaction_type: type,
    });
    return res.data;
  },

  // ── Recommendations ─────────────────────────────────────────────────
  getRecommendations: async (limit: number = 20, recompute: boolean = false): Promise<Recommendation[]> => {
    const res = await apiClient.get('/recommendations', {
      params: { limit, recompute },
    });
    return res.data;
  },
  recomputeRecommendations: async (limit: number = 50): Promise<Recommendation[]> => {
    const res = await apiClient.post('/recommendations/recompute', null, {
      params: { limit },
    });
    return res.data;
  },
  getJobRecommendationDetail: async (jobId: number): Promise<RecommendationDetail> => {
    const res = await apiClient.get(`/recommendations/job/${jobId}`);
    return res.data;
  },

  // ── Skills ──────────────────────────────────────────────────────────
  searchSkills: async (query: string) => {
    const res = await apiClient.get('/skills/search', { params: { q: query } });
    return res.data;
  },
  getSkillCategories: async () => {
    const res = await apiClient.get('/skills/categories');
    return res.data;
  },

  // ── Admin ───────────────────────────────────────────────────────────
  getAdminStats: async () => {
    const res = await apiClient.get('/admin/stats');
    return res.data;
  },
  getJobSources: async () => {
    const res = await apiClient.get('/admin/sources');
    return res.data;
  },
  triggerCollection: async (maxPerSource: number = 50) => {
    const res = await apiClient.post('/admin/collect', null, {
      params: { max_per_source: maxPerSource },
    });
    return res.data;
  },
  getDuplicates: async () => {
    const res = await apiClient.get('/admin/duplicates');
    return res.data;
  },
};
