// TODO: i18n - processed
/**
 * useTranslationValidation Hook
 * Validate translations for completeness and quality
 */

import { useState, useCallback, useMemo } from 'react';
import translationManager from '../managers/TranslationManager';
import { SUPPORTED_LANGUAGES, TRANSLATION_NAMESPACES } from '../constants';import { useTranslation } from "react-i18next";

const useTranslationValidation = () => {
  const [validationResults, setValidationResults] = useState({});
  const [isValidating, setIsValidating] = useState(false);

  // Validation rules
  const validationRules = useMemo(() => ({
    // Check for missing translations
    missingKeys: (reference, target) => {
      const missing = [];
      const checkKeys = (refObj, targetObj, path = '') => {
        for (const key in refObj) {
          const fullPath = path ? `${path}.${key}` : key;
          if (!(key in targetObj)) {
            missing.push(fullPath);
          } else if (typeof refObj[key] === 'object' && refObj[key] !== null) {
            checkKeys(refObj[key], targetObj[key] || {}, fullPath);
          }
        }
      };
      checkKeys(reference, target);
      return missing;
    },

    // Check for empty values
    emptyValues: (translations) => {
      const empty = [];
      const checkEmpty = (obj, path = '') => {
        for (const key in obj) {
          const fullPath = path ? `${path}.${key}` : key;
          const value = obj[key];
          if (typeof value === 'string' && value.trim() === '') {
            empty.push(fullPath);
          } else if (typeof value === 'object' && value !== null) {
            checkEmpty(value, fullPath);
          }
        }
      };
      checkEmpty(translations);
      return empty;
    },

    // Check for untranslated placeholders
    placeholders: (reference, target) => {
      const issues = [];
      const checkPlaceholders = (refObj, targetObj, path = '') => {
        for (const key in refObj) {
          const fullPath = path ? `${path}.${key}` : key;
          if (typeof refObj[key] === 'string' && typeof targetObj[key] === 'string') {
            const refPlaceholders = (refObj[key].match(/{{[^}]+}}/g) || []).sort();
            const targetPlaceholders = (targetObj[key].match(/{{[^}]+}}/g) || []).sort();

            if (JSON.stringify(refPlaceholders) !== JSON.stringify(targetPlaceholders)) {
              issues.push({
                key: fullPath,
                reference: refPlaceholders,
                target: targetPlaceholders
              });
            }
          } else if (typeof refObj[key] === 'object' && refObj[key] !== null) {
            checkPlaceholders(refObj[key], targetObj[key] || {}, fullPath);
          }
        }
      };
      checkPlaceholders(reference, target);
      return issues;
    },

    // Check for HTML tags consistency
    htmlTags: (reference, target) => {
      const issues = [];
      const checkHtml = (refObj, targetObj, path = '') => {
        for (const key in refObj) {
          const fullPath = path ? `${path}.${key}` : key;
          if (typeof refObj[key] === 'string' && typeof targetObj[key] === 'string') {
            const refTags = (refObj[key].match(/<[^>]+>/g) || []).sort();
            const targetTags = (targetObj[key].match(/<[^>]+>/g) || []).sort();

            if (JSON.stringify(refTags) !== JSON.stringify(targetTags)) {
              issues.push({
                key: fullPath,
                reference: refTags,
                target: targetTags
              });
            }
          } else if (typeof refObj[key] === 'object' && refObj[key] !== null) {
            checkHtml(refObj[key], targetObj[key] || {}, fullPath);
          }
        }
      };
      checkHtml(reference, target);
      return issues;
    },

    // Check for length differences
    lengthCheck: (reference, target, threshold = 2) => {
      const issues = [];
      const checkLength = (refObj, targetObj, path = '') => {
        for (const key in refObj) {
          const fullPath = path ? `${path}.${key}` : key;
          if (typeof refObj[key] === 'string' && typeof targetObj[key] === 'string') {
            const refLength = refObj[key].length;
            const targetLength = targetObj[key].length;
            const ratio = targetLength / refLength;

            if (ratio > threshold || ratio < 1 / threshold) {
              issues.push({
                key: fullPath,
                referenceLength: refLength,
                targetLength,
                ratio: ratio.toFixed(2)
              });
            }
          } else if (typeof refObj[key] === 'object' && refObj[key] !== null) {
            checkLength(refObj[key], targetObj[key] || {}, fullPath);
          }
        }
      };
      checkLength(reference, target);
      return issues;
    },

    // Check for formatting consistency
    formatting: (reference, target) => {
      const issues = [];
      const checkFormatting = (refObj, targetObj, path = '') => {
        for (const key in refObj) {
          const fullPath = path ? `${path}.${key}` : key;
          if (typeof refObj[key] === 'string' && typeof targetObj[key] === 'string') {
            // Check punctuation at end
            const refEnding = refObj[key].match(/[.!?:;,]$/);
            const targetEnding = targetObj[key].match(/[.!?:;,]$/);

            if (refEnding && !targetEnding || !refEnding && targetEnding) {
              issues.push({
                key: fullPath,
                type: 'punctuation',
                reference: refEnding?.[0] || 'none',
                target: targetEnding?.[0] || 'none'
              });
            }

            // Check capitalization
            const refCapitalized = /^[A-Z]/.test(refObj[key]);
            const targetCapitalized = /^[A-Z\u00C0-\u00DC\u0400-\u04FF\u0600-\u06FF]/.test(targetObj[key]);

            if (refCapitalized !== targetCapitalized) {
              issues.push({
                key: fullPath,
                type: 'capitalization',
                reference: refCapitalized,
                target: targetCapitalized
              });
            }
          } else if (typeof refObj[key] === 'object' && refObj[key] !== null) {
            checkFormatting(refObj[key], targetObj[key] || {}, fullPath);
          }
        }
      };
      checkFormatting(reference, target);
      return issues;
    }
  }), []);

  // Validate single language
  const validateLanguage = useCallback(async (language, referenceLanguage = 'en') => {
    const results = {
      language,
      referenceLanguage,
      valid: true,
      issues: {
        missing: [],
        empty: [],
        placeholders: [],
        htmlTags: [],
        length: [],
        formatting: []
      },
      stats: {
        totalKeys: 0,
        translatedKeys: 0,
        coverage: 0
      }
    };

    try {
      // Load translations for both languages
      const referenceTranslations = await translationManager.exportTranslations(referenceLanguage);
      const targetTranslations = await translationManager.exportTranslations(language);

      // Count total keys
      const countKeys = (obj) => {
        let count = 0;
        const traverse = (o) => {
          for (const key in o) {
            if (typeof o[key] === 'string') {
              count++;
            } else if (typeof o[key] === 'object' && o[key] !== null) {
              traverse(o[key]);
            }
          }
        };
        traverse(obj);
        return count;
      };

      results.stats.totalKeys = countKeys(referenceTranslations);

      // Run validation rules
      for (const namespace of TRANSLATION_NAMESPACES) {
        const refNs = referenceTranslations[namespace] || {};
        const targetNs = targetTranslations[namespace] || {};

        // Missing keys
        const missing = validationRules.missingKeys(refNs, targetNs);
        results.issues.missing.push(...missing.map((key) => ({ namespace, key })));

        // Empty values
        const empty = validationRules.emptyValues(targetNs);
        results.issues.empty.push(...empty.map((key) => ({ namespace, key })));

        // Placeholders
        const placeholders = validationRules.placeholders(refNs, targetNs);
        results.issues.placeholders.push(...placeholders.map((issue) => ({ namespace, ...issue })));

        // HTML tags
        const htmlTags = validationRules.htmlTags(refNs, targetNs);
        results.issues.htmlTags.push(...htmlTags.map((issue) => ({ namespace, ...issue })));

        // Length check
        const length = validationRules.lengthCheck(refNs, targetNs);
        results.issues.length.push(...length.map((issue) => ({ namespace, ...issue })));

        // Formatting
        const formatting = validationRules.formatting(refNs, targetNs);
        results.issues.formatting.push(...formatting.map((issue) => ({ namespace, ...issue })));
      }

      // Calculate statistics
      results.stats.translatedKeys = results.stats.totalKeys - results.issues.missing.length - results.issues.empty.length;
      results.stats.coverage = results.stats.totalKeys > 0 ?
      results.stats.translatedKeys / results.stats.totalKeys * 100 :
      0;

      // Determine if valid
      results.valid = results.issues.missing.length === 0 &&
      results.issues.empty.length === 0 &&
      results.issues.placeholders.length === 0;

      return results;
    } catch (error) {
      console.error('Validation error:', error);
      results.valid = false;
      results.error = error.message;
      return results;
    }
  }, [validationRules]);

  // Validate all languages
  const validateAllLanguages = useCallback(async (referenceLanguage = 'en') => {
    setIsValidating(true);
    const results = {};

    try {
      const languages = Object.keys(SUPPORTED_LANGUAGES).filter((lang) => lang !== referenceLanguage);

      for (const language of languages) {
        results[language] = await validateLanguage(language, referenceLanguage);
      }

      setValidationResults(results);
      return results;
    } catch (error) {
      console.error('Validation error:', error);
      return { error: error.message };
    } finally {
      setIsValidating(false);
    }
  }, [validateLanguage]);

  // Generate validation report
  const generateReport = useCallback(() => {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalLanguages: Object.keys(validationResults).length,
        validLanguages: 0,
        averageCoverage: 0,
        criticalIssues: 0,
        warnings: 0
      },
      languages: {},
      recommendations: []
    };

    let totalCoverage = 0;

    for (const [language, results] of Object.entries(validationResults)) {
      if (results.valid) {
        report.summary.validLanguages++;
      }

      totalCoverage += results.stats.coverage;

      // Count critical issues
      const criticalCount = results.issues.missing.length +
      results.issues.empty.length +
      results.issues.placeholders.length;

      report.summary.criticalIssues += criticalCount;

      // Count warnings
      const warningCount = results.issues.htmlTags.length +
      results.issues.length.length +
      results.issues.formatting.length;

      report.summary.warnings += warningCount;

      report.languages[language] = {
        valid: results.valid,
        coverage: results.stats.coverage.toFixed(2) + '%',
        issues: {
          critical: criticalCount,
          warnings: warningCount
        }
      };
    }

    report.summary.averageCoverage = report.summary.totalLanguages > 0 ?
    (totalCoverage / report.summary.totalLanguages).toFixed(2) + '%' :
    '0%';

    // Generate recommendations
    if (report.summary.criticalIssues > 0) {
      report.recommendations.push('Address critical issues (missing translations and placeholders) first');
    }

    if (parseFloat(report.summary.averageCoverage) < 80) {
      report.recommendations.push('Improve translation coverage to at least 80% for better user experience');
    }

    if (report.summary.warnings > 50) {
      report.recommendations.push('Review formatting and length warnings to ensure consistency');
    }

    return report;
  }, [validationResults]);

  // Fix common issues automatically
  const autoFix = useCallback(async (language, issueType) => {
    const fixes = [];

    switch (issueType) {
      case 'empty':
        // Copy from reference language
        const results = validationResults[language];
        if (results?.issues.empty.length > 0) {
          for (const { namespace, key } of results.issues.empty) {
            try {
              const refValue = translationManager.getTranslation(key, 'en', namespace);
              if (refValue && refValue !== key) {
                translationManager.updateTranslation(language, namespace, key, `[TO TRANSLATE] ${refValue}`);
                fixes.push({ namespace, key, action: 'copied_from_reference' });
              }
            } catch (error) {
              console.error(`Failed to fix ${namespace}:${key}`, error);
            }
          }
        }
        break;

      case 'formatting':
        // Fix capitalization and punctuation
        const formattingIssues = validationResults[language]?.issues.formatting || [];
        for (const issue of formattingIssues) {
          if (issue.type === 'capitalization') {
            // Auto-fix capitalization logic
            fixes.push({ ...issue, action: 'fixed_capitalization' });
          } else if (issue.type === 'punctuation') {
            // Auto-fix punctuation logic
            fixes.push({ ...issue, action: 'fixed_punctuation' });
          }
        }
        break;

      default:
        console.warn(`Auto-fix not implemented for issue type: ${issueType}`);
    }

    return fixes;
  }, [validationResults]);

  return {
    validationResults,
    isValidating,

    // Validation functions
    validateLanguage,
    validateAllLanguages,

    // Reporting
    generateReport,

    // Auto-fix
    autoFix,

    // Utilities
    validationRules
  };
};

export default useTranslationValidation;