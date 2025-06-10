// TODO: i18n - processed
import api from '@/lib/api';
/**
 * Get a list of beneficiaries with pagination and filters
 * 
 * @param {Object} params - Query parameters
 * @param {number} params.page - Page number
 * @param {number} params.per_page - Items per page
 * @param {string} params.sort_by - Field to sort by
 * @param {string} params.sort_dir - Sort direction (asc/desc)
 * @param {string} params.status - Filter by status
 * @param {string} params.search - Search term
 * @returns {Promise<Object>} Beneficiaries data with pagination
 */import { useTranslation } from "react-i18next";
export const getBeneficiaries = async (params = {}) => {
  try {
    const response = await api.get('/api/beneficiaries', { params });
    return {
      data: response.data.items || response.data.data || [],
      total: response.data.total || 0,
      page: response.data.page || 1,
      totalPages: response.data.pages || response.data.total_pages || 1
    };
  } catch (error) {
    console.error('Error fetching beneficiaries:', error);
    throw error;
  }
};
/**
 * Get a single beneficiary by ID
 * 
 * @param {number} id - Beneficiary ID
 * @returns {Promise<Object>} Beneficiary data
 */
export const getBeneficiary = async (id) => {
  try {
    const response = await api.get(`/api/beneficiaries/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching beneficiary ${id}:`, error);
    throw error;
  }
};
/**
 * Create a new beneficiary
 * 
 * @param {Object} data - Beneficiary data
 * @returns {Promise<Object>} Created beneficiary
 */
export const createBeneficiary = async (data) => {
  try {
    const response = await api.post('/api/beneficiaries', data);
    return response.data;
  } catch (error) {
    console.error('Error creating beneficiary:', error);
    throw error;
  }
};
/**
 * Update an existing beneficiary
 * 
 * @param {number} id - Beneficiary ID
 * @param {Object} data - Updated beneficiary data
 * @returns {Promise<Object>} Updated beneficiary
 */
export const updateBeneficiary = async (id, data) => {
  try {
    const response = await api.put(`/api/beneficiaries/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating beneficiary ${id}:`, error);
    throw error;
  }
};
/**
 * Delete a beneficiary
 * 
 * @param {number} id - Beneficiary ID
 * @returns {Promise<Object>} Response data
 */
export const deleteBeneficiary = async (id) => {
  try {
    const response = await api.delete(`/api/beneficiaries/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting beneficiary ${id}:`, error);
    throw error;
  }
};
/**
 * Export beneficiaries to a file format
 * 
 * @param {string} format - Export format (csv, xlsx)
 * @param {Object} filters - Export filters
 * @returns {Promise<Blob>} File blob
 */
export const exportBeneficiaries = async (format = 'csv', filters = {}) => {
  try {
    const response = await api.get(`/api/beneficiaries/export`, {
      params: { format, ...filters },
      responseType: 'blob'
    });
    // Create a download link and trigger it
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `beneficiaries.${format}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    return response.data;
  } catch (error) {
    console.error('Error exporting beneficiaries:', error);
    throw error;
  }
};