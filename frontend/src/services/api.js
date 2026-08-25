import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productsAPI = {
  getAll: (params) => api.get('/products/', { params }),
  getById: (id) => api.get(`/products/${id}/`),
  create: (data) => api.post('/products/', data),
  update: (id, data) => api.put(`/products/${id}/`, data),
  delete: (id) => api.delete(`/products/${id}/`),
  importProducts: (formData) => api.post('/products/import_products/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  exportProducts: () => api.get('/products/export_products/', { responseType: 'blob' }),
};

export const classificationsAPI = {
  getAll: (params) => api.get('/classifications/', { params }),
  getById: (id) => api.get(`/classifications/${id}/`),
  classify: (data) => api.post('/classifications/classify/', data),
  batchClassify: (data) => api.post('/classifications/batch_classify/', data),
  approve: (id, data) => api.post(`/classifications/${id}/approve/`, data),
  reject: (id, data) => api.post(`/classifications/${id}/reject/`, data),
  reassign: (id, data) => api.post(`/classifications/${id}/reassign/`, data),
  batchApprove: (data) => api.post('/classifications/batch_approve/', data),
};

export const taxonomyAPI = {
  getAll: (params) => api.get('/taxonomy/', { params }),
  getTree: () => api.get('/taxonomy/tree/'),
  getById: (id) => api.get(`/taxonomy/${id}/`),
};

export const batchesAPI = {
  getAll: (params) => api.get('/batches/', { params }),
  getById: (id) => api.get(`/batches/${id}/`),
  create: (data) => api.post('/batches/', data),
  start: (id) => api.post(`/batches/${id}/start/`),
  progress: (id) => api.get(`/batches/${id}/progress/`),
};

export const statsAPI = {
  getStats: () => api.get('/stats/'),
};

export default api;