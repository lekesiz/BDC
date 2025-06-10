// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Validation Utilities
 * 
 * Common validation functions for the reporting system
 */

// Validate report configuration
export const validateReportConfig = (config) => {
  const errors = [];
  const warnings = [];

  // Check basic structure
  if (!config || typeof config !== 'object') {
    return {
      isValid: false,
      errors: ['Invalid configuration object'],
      warnings: []
    };
  }

  // Validate fields
  if (!config.fields || !Array.isArray(config.fields)) {
    errors.push('Fields array is required');
  } else if (config.fields.length === 0) {
    errors.push('At least one field must be selected');
  } else {
    config.fields.forEach((field, index) => {
      const fieldErrors = validateField(field, index + 1);
      errors.push(...fieldErrors);
    });

    // Check for performance issues
    if (config.fields.length > 50) {
      warnings.push(`Large number of fields (${config.fields.length}) may impact performance`);
    }
  }

  // Validate filters
  if (config.filters && Array.isArray(config.filters)) {
    config.filters.forEach((filter, index) => {
      const filterErrors = validateFilter(filter, index + 1);
      errors.push(...filterErrors);
    });

    if (config.filters.length > 20) {
      warnings.push(`Large number of filters (${config.filters.length}) may impact performance`);
    }
  }

  // Validate grouping
  if (config.grouping && Array.isArray(config.grouping)) {
    config.grouping.forEach((group, index) => {
      const groupErrors = validateGrouping(group, index + 1);
      errors.push(...groupErrors);
    });
  }

  // Validate sorting
  if (config.sorting && Array.isArray(config.sorting)) {
    config.sorting.forEach((sort, index) => {
      const sortErrors = validateSorting(sort, index + 1);
      errors.push(...sortErrors);
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

// Validate individual field
export const validateField = (field, position) => {
  const errors = [];

  if (!field || typeof field !== 'object') {
    errors.push(`Field ${position}: Invalid field object`);
    return errors;
  }

  if (!field.field || typeof field.field !== 'string') {
    errors.push(`Field ${position}: Field name is required`);
  }

  if (!field.source || typeof field.source !== 'string') {
    errors.push(`Field ${position}: Data source is required`);
  }

  if (!field.type || typeof field.type !== 'string') {
    errors.push(`Field ${position}: Field type is required`);
  }

  // Validate aggregation if present
  if (field.aggregation) {
    const validAggregations = ['sum', 'count', 'avg', 'min', 'max', 'distinct'];
    if (!validAggregations.includes(field.aggregation)) {
      errors.push(`Field ${position}: Invalid aggregation type '${field.aggregation}'`);
    }
  }

  return errors;
};

// Validate filter
export const validateFilter = (filter, position) => {
  const errors = [];

  if (!filter || typeof filter !== 'object') {
    errors.push(`Filter ${position}: Invalid filter object`);
    return errors;
  }

  if (!filter.field || typeof filter.field !== 'string') {
    errors.push(`Filter ${position}: Field is required`);
  }

  if (!filter.operator || typeof filter.operator !== 'string') {
    errors.push(`Filter ${position}: Operator is required`);
  } else {
    const validOperators = [
    'equals', 'not_equals', 'contains', 'not_contains',
    'starts_with', 'ends_with', 'greater_than', 'less_than',
    'greater_equal', 'less_equal', 'between', 'in', 'not_in',
    'is_null', 'is_not_null'];


    if (!validOperators.includes(filter.operator)) {
      errors.push(`Filter ${position}: Invalid operator '${filter.operator}'`);
    }
  }

  // Check if value is required for the operator
  const operatorsWithoutValue = ['is_null', 'is_not_null'];
  if (!operatorsWithoutValue.includes(filter.operator)) {
    if (filter.value === undefined || filter.value === null || filter.value === '') {
      errors.push(`Filter ${position}: Value is required for operator '${filter.operator}'`);
    }
  }

  // Validate value format for specific operators
  if (filter.operator === 'between') {
    if (!Array.isArray(filter.value) || filter.value.length !== 2) {
      errors.push(`Filter ${position}: 'between' operator requires an array with exactly 2 values`);
    }
  }

  if (filter.operator === 'in' || filter.operator === 'not_in') {
    if (!Array.isArray(filter.value)) {
      errors.push(`Filter ${position}: '${filter.operator}' operator requires an array of values`);
    }
  }

  return errors;
};

// Validate grouping
export const validateGrouping = (group, position) => {
  const errors = [];

  if (!group || typeof group !== 'object') {
    errors.push(`Grouping ${position}: Invalid grouping object`);
    return errors;
  }

  if (!group.field || typeof group.field !== 'string') {
    errors.push(`Grouping ${position}: Field is required`);
  }

  if (!group.source || typeof group.source !== 'string') {
    errors.push(`Grouping ${position}: Data source is required`);
  }

  return errors;
};

// Validate sorting
export const validateSorting = (sort, position) => {
  const errors = [];

  if (!sort || typeof sort !== 'object') {
    errors.push(`Sorting ${position}: Invalid sorting object`);
    return errors;
  }

  if (!sort.field || typeof sort.field !== 'string') {
    errors.push(`Sorting ${position}: Field is required`);
  }

  if (!sort.source || typeof sort.source !== 'string') {
    errors.push(`Sorting ${position}: Data source is required`);
  }

  if (sort.direction && !['asc', 'desc'].includes(sort.direction)) {
    errors.push(`Sorting ${position}: Direction must be 'asc' or 'desc'`);
  }

  return errors;
};

// Validate dashboard configuration
export const validateDashboardConfig = (config) => {
  const errors = [];
  const warnings = [];

  if (!config || typeof config !== 'object') {
    return {
      isValid: false,
      errors: ['Invalid dashboard configuration'],
      warnings: []
    };
  }

  if (!config.name || typeof config.name !== 'string' || config.name.trim().length === 0) {
    errors.push('Dashboard name is required');
  }

  // Validate widgets
  if (config.widgets && Array.isArray(config.widgets)) {
    config.widgets.forEach((widget, index) => {
      const widgetErrors = validateWidget(widget, index + 1);
      errors.push(...widgetErrors);
    });

    if (config.widgets.length > 20) {
      warnings.push(`Large number of widgets (${config.widgets.length}) may impact performance`);
    }
  }

  // Validate layout
  if (config.layout && typeof config.layout === 'object') {
    const layoutErrors = validateLayout(config.layout);
    errors.push(...layoutErrors);
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

// Validate widget configuration
export const validateWidget = (widget, position) => {
  const errors = [];

  if (!widget || typeof widget !== 'object') {
    errors.push(`Widget ${position}: Invalid widget object`);
    return errors;
  }

  if (!widget.type || typeof widget.type !== 'string') {
    errors.push(`Widget ${position}: Widget type is required`);
  } else {
    const validTypes = ['chart', 'metric', 'table', 'map', 'calendar', 'progress', 'text'];
    if (!validTypes.includes(widget.type)) {
      errors.push(`Widget ${position}: Invalid widget type '${widget.type}'`);
    }
  }

  // Validate widget-specific configuration
  if (widget.config && typeof widget.config === 'object') {
    const configErrors = validateWidgetConfig(widget.type, widget.config, position);
    errors.push(...configErrors);
  }

  return errors;
};

// Validate widget-specific configuration
export const validateWidgetConfig = (widgetType, config, position) => {
  const errors = [];

  switch (widgetType) {
    case 'chart':
      if (!config.chart_type) {
        errors.push(`Widget ${position}: Chart type is required`);
      }
      if (!config.data_source) {
        errors.push(`Widget ${position}: Data source is required`);
      }
      if (!config.x_axis) {
        errors.push(`Widget ${position}: X-axis field is required`);
      }
      if (!config.y_axis) {
        errors.push(`Widget ${position}: Y-axis field is required`);
      }
      break;

    case 'metric':
      if (!config.data_source) {
        errors.push(`Widget ${position}: Data source is required`);
      }
      if (!config.metric_field) {
        errors.push(`Widget ${position}: Metric field is required`);
      }
      break;

    case 'table':
      if (!config.data_source) {
        errors.push(`Widget ${position}: Data source is required`);
      }
      if (!config.columns || !Array.isArray(config.columns) || config.columns.length === 0) {
        errors.push(`Widget ${position}: At least one column is required`);
      }
      break;

    case 'map':
      if (!config.data_source) {
        errors.push(`Widget ${position}: Data source is required`);
      }
      if (!config.location_field) {
        errors.push(`Widget ${position}: Location field is required`);
      }
      break;

    case 'calendar':
      if (!config.data_source) {
        errors.push(`Widget ${position}: Data source is required`);
      }
      if (!config.date_field) {
        errors.push(`Widget ${position}: Date field is required`);
      }
      if (!config.title_field) {
        errors.push(`Widget ${position}: Title field is required`);
      }
      break;

    case 'progress':
      if (!config.data_source) {
        errors.push(`Widget ${position}: Data source is required`);
      }
      if (!config.current_field) {
        errors.push(`Widget ${position}: Current value field is required`);
      }
      break;

    case 'text':
      if (!config.content || typeof config.content !== 'string' || config.content.trim().length === 0) {
        errors.push(`Widget ${position}: Content is required`);
      }
      break;
  }

  return errors;
};

// Validate layout configuration
export const validateLayout = (layout) => {
  const errors = [];

  if (layout.type && !['grid', 'fixed', 'flow'].includes(layout.type)) {
    errors.push("Invalid layout type. Must be 'grid', 'fixed', or 'flow'");
  }

  if (layout.columns && (typeof layout.columns !== 'number' || layout.columns < 1 || layout.columns > 24)) {
    errors.push('Layout columns must be a number between 1 and 24');
  }

  return errors;
};

// Validate export configuration
export const validateExportConfig = (format, config) => {
  const errors = [];
  const warnings = [];

  if (!format || typeof format !== 'string') {
    errors.push('Export format is required');
    return { isValid: false, errors, warnings };
  }

  const validFormats = ['pdf', 'excel', 'csv', 'powerpoint', 'word', 'json', 'xml', 'png'];
  if (!validFormats.includes(format)) {
    errors.push(`Invalid export format '${format}'`);
  }

  if (!config || typeof config !== 'object') {
    return { isValid: errors.length === 0, errors, warnings };
  }

  // Format-specific validations
  switch (format) {
    case 'csv':
      if (config.delimiter && typeof config.delimiter !== 'string') {
        errors.push('CSV delimiter must be a string');
      }
      if (config.delimiter && config.delimiter.length !== 1) {
        errors.push('CSV delimiter must be a single character');
      }
      break;

    case 'pdf':
      if (config.page_size && !['A4', 'Letter', 'Legal', 'A3'].includes(config.page_size)) {
        errors.push('Invalid PDF page size');
      }
      if (config.orientation && !['portrait', 'landscape'].includes(config.orientation)) {
        errors.push('Invalid PDF orientation');
      }
      break;

    case 'json':
      if (config.indent && (typeof config.indent !== 'number' || config.indent < 0)) {
        errors.push('JSON indent must be a non-negative number');
      }
      break;
  }

  // File name validation
  if (config.file_name && typeof config.file_name === 'string') {
    const invalidChars = /[<>:"|?*\\\/]/;
    if (invalidChars.test(config.file_name)) {
      errors.push('File name contains invalid characters');
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

// Validate schedule configuration
export const validateScheduleConfig = (config) => {
  const errors = [];
  const warnings = [];

  if (!config || typeof config !== 'object') {
    return {
      isValid: false,
      errors: ['Invalid schedule configuration'],
      warnings: []
    };
  }

  if (!config.name || typeof config.name !== 'string' || config.name.trim().length === 0) {
    errors.push('Schedule name is required');
  }

  if (!config.report_config || typeof config.report_config !== 'object') {
    errors.push('Report configuration is required');
  }

  if (!config.delivery_config || typeof config.delivery_config !== 'object') {
    errors.push('Delivery configuration is required');
  }

  // Validate schedule configuration
  if (config.schedule_config && typeof config.schedule_config === 'object') {
    const scheduleErrors = validateScheduleFrequency(config.schedule_config);
    errors.push(...scheduleErrors);
  }

  // Validate delivery configuration
  if (config.delivery_config && typeof config.delivery_config === 'object') {
    const deliveryErrors = validateDeliveryConfig(config.delivery_config);
    errors.push(...deliveryErrors);
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

// Validate schedule frequency
export const validateScheduleFrequency = (scheduleConfig) => {
  const errors = [];

  if (!scheduleConfig.type) {
    errors.push('Schedule type is required');
    return errors;
  }

  const validTypes = ['manual', 'once', 'daily', 'weekly', 'monthly', 'cron'];
  if (!validTypes.includes(scheduleConfig.type)) {
    errors.push(`Invalid schedule type '${scheduleConfig.type}'`);
  }

  if (scheduleConfig.type === 'cron') {
    if (!scheduleConfig.cron_expression) {
      errors.push('Cron expression is required for cron schedule type');
    } else {
      // Basic cron validation (5 or 6 parts)
      const parts = scheduleConfig.cron_expression.split(' ');
      if (parts.length < 5 || parts.length > 6) {
        errors.push('Invalid cron expression format');
      }
    }
  }

  return errors;
};

// Validate delivery configuration
export const validateDeliveryConfig = (deliveryConfig) => {
  const errors = [];

  if (!deliveryConfig.method) {
    errors.push('Delivery method is required');
    return errors;
  }

  const validMethods = ['email', 'webhook', 'ftp', 'filesystem'];
  if (!validMethods.includes(deliveryConfig.method)) {
    errors.push(`Invalid delivery method '${deliveryConfig.method}'`);
  }

  switch (deliveryConfig.method) {
    case 'email':
      if (!deliveryConfig.recipients || !Array.isArray(deliveryConfig.recipients) || deliveryConfig.recipients.length === 0) {
        errors.push('Email recipients are required');
      } else {
        deliveryConfig.recipients.forEach((email, index) => {
          if (!isValidEmail(email)) {
            errors.push(`Invalid email address at position ${index + 1}: ${email}`);
          }
        });
      }
      break;

    case 'webhook':
      if (!deliveryConfig.webhook_url) {
        errors.push('Webhook URL is required');
      } else if (!isValidUrl(deliveryConfig.webhook_url)) {
        errors.push('Invalid webhook URL');
      }
      break;

    case 'ftp':
      if (!deliveryConfig.ftp_host) {
        errors.push('FTP host is required');
      }
      if (!deliveryConfig.ftp_user) {
        errors.push('FTP username is required');
      }
      if (!deliveryConfig.ftp_password) {
        errors.push('FTP password is required');
      }
      break;

    case 'filesystem':
      if (!deliveryConfig.target_path) {
        errors.push('Target path is required for filesystem delivery');
      }
      break;
  }

  return errors;
};

// Helper functions
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Sanitize input data
export const sanitizeString = (str) => {
  if (typeof str !== 'string') return str;

  return str.
  replace(/[<>]/g, '') // Remove < and >
  .replace(/javascript:/gi, '') // Remove javascript: protocol
  .replace(/on\w+=/gi, '') // Remove event handlers
  .trim();
};

// Validate data limits
export const validateDataLimits = (config) => {
  const warnings = [];
  const errors = [];

  // Check field count
  if (config.fields && config.fields.length > 100) {
    errors.push('Maximum 100 fields allowed');
  } else if (config.fields && config.fields.length > 50) {
    warnings.push('Large number of fields may impact performance');
  }

  // Check filter complexity
  if (config.filters && config.filters.length > 50) {
    errors.push('Maximum 50 filters allowed');
  } else if (config.filters && config.filters.length > 20) {
    warnings.push('Large number of filters may impact performance');
  }

  return { errors, warnings };
};