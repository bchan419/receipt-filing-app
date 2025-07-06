import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for OCR processing
});

// API service functions
export const apiService = {
  // Test API connection
  async testConnection() {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      throw new Error(`API connection failed: ${error.message}`);
    }
  },

  // Get available categories
  async getCategories() {
    try {
      const response = await api.get('/categories');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch categories: ${error.message}`);
    }
  },

  // Upload and process receipt images
  async uploadReceipts(files) {
    try {
      const formData = new FormData();
      
      // Add each file to FormData
      files.forEach((file, index) => {
        formData.append('files', file);
      });

      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Show upload progress
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      });

      return response.data;
    } catch (error) {
      if (error.response?.data) {
        throw new Error(`Upload failed: ${error.response.data.detail || error.message}`);
      }
      throw new Error(`Upload failed: ${error.message}`);
    }
  },

  // Export receipts to CSV
  async exportToCSV(receipts) {
    try {
      const response = await api.post('/export/csv', { receipts }, {
        responseType: 'blob',
      });
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'receipts.csv';
      link.click();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      throw new Error(`CSV export failed: ${error.message}`);
    }
  },

  // Export receipts to Excel
  async exportToExcel(receipts) {
    try {
      const response = await api.post('/export/excel', { receipts }, {
        responseType: 'blob',
      });
      
      // Create download link
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'receipts.xlsx';
      link.click();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      throw new Error(`Excel export failed: ${error.message}`);
    }
  },

  // Get summary statistics
  async getSummary(receipts) {
    try {
      const response = await api.post('/summary', receipts);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get summary: ${error.message}`);
    }
  }
};

export default api;