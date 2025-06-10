// TODO: i18n - processed
/**
 * useReportBuilder Hook
 * 
 * Custom hook for managing report builder state and operations
 */

import { useState, useCallback, useEffect } from 'react';
import ReportingAPI from '../services/reportingAPI';import { useTranslation } from "react-i18next";

const useReportBuilder = (initialConfig = null) => {
  const [reportConfig, setReportConfig] = useState(initialConfig || {
    fields: [],
    filters: [],
    grouping: [],
    sorting: []
  });

  const [availableFields, setAvailableFields] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState([]);

  // Load available fields from the API
  const loadAvailableFields = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fields = await ReportingAPI.getAvailableFields();
      setAvailableFields(fields);
    } catch (err) {
      setError(err);
      console.error('Failed to load available fields:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update report configuration
  const updateReportConfig = useCallback((newConfig) => {
    setReportConfig(newConfig);

    // Validate the new configuration
    const validation = validateReportConfig(newConfig);
    setValidationErrors(validation.errors || []);
  }, []);

  // Add a field to the report
  const addField = useCallback((field) => {
    const newField = {
      ...field,
      id: `${field.source}_${field.field}_${Date.now()}`,
      alias: field.alias || field.name || field.field
    };

    setReportConfig((prev) => ({
      ...prev,
      fields: [...prev.fields, newField]
    }));
  }, []);

  // Remove a field from the report
  const removeField = useCallback((fieldId) => {
    setReportConfig((prev) => ({
      ...prev,
      fields: prev.fields.filter((f) => f.id !== fieldId)
    }));
  }, []);

  // Update a specific field
  const updateField = useCallback((fieldId, updates) => {
    setReportConfig((prev) => ({
      ...prev,
      fields: prev.fields.map((f) =>
      f.id === fieldId ? { ...f, ...updates } : f
      )
    }));
  }, []);

  // Add a filter
  const addFilter = useCallback((filter) => {
    const newFilter = {
      ...filter,
      id: `filter_${Date.now()}`
    };

    setReportConfig((prev) => ({
      ...prev,
      filters: [...prev.filters, newFilter]
    }));
  }, []);

  // Remove a filter
  const removeFilter = useCallback((filterId) => {
    setReportConfig((prev) => ({
      ...prev,
      filters: prev.filters.filter((f) => f.id !== filterId)
    }));
  }, []);

  // Update a filter
  const updateFilter = useCallback((filterId, updates) => {
    setReportConfig((prev) => ({
      ...prev,
      filters: prev.filters.map((f) =>
      f.id === filterId ? { ...f, ...updates } : f
      )
    }));
  }, []);

  // Save report
  const saveReport = useCallback(async (reportData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await ReportingAPI.saveReport(reportData);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Preview report
  const previewReport = useCallback(async (reportData, sampleSize = 10) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await ReportingAPI.previewReport(reportData, sampleSize);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Export report
  const exportReport = useCallback(async (reportData, format, options = {}) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await ReportingAPI.exportReport(reportData, format, options);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    reportConfig,
    availableFields,
    isLoading,
    error,
    validationErrors,
    updateReportConfig,
    addField,
    removeField,
    updateField,
    addFilter,
    removeFilter,
    updateFilter,
    loadAvailableFields,
    saveReport,
    previewReport,
    exportReport
  };
};

// Validation helper function
function validateReportConfig(config) {
  const errors = [];

  // Check if at least one field is selected
  if (!config.fields || config.fields.length === 0) {
    errors.push('At least one field must be selected');
  }

  // Validate field configurations
  config.fields?.forEach((field, index) => {
    if (!field.field) {
      errors.push(`Field ${index + 1}: Field name is required`);
    }
    if (!field.source) {
      errors.push(`Field ${index + 1}: Data source is required`);
    }
  });

  // Validate filters
  config.filters?.forEach((filter, index) => {
    if (!filter.field) {
      errors.push(`Filter ${index + 1}: Field is required`);
    }
    if (!filter.operator) {
      errors.push(`Filter ${index + 1}: Operator is required`);
    }
    if (filter.value === undefined || filter.value === null || filter.value === '') {
      errors.push(`Filter ${index + 1}: Value is required`);
    }
  });

  return {
    isValid: errors.length === 0,
    errors
  };
}

export default useReportBuilder;