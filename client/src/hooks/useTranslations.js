import { useTranslation } from 'react-i18next';
/**
 * Custom hook for using translations in the BDC application
 * Provides typed translation keys and helper functions
 */
export const useTranslations = () => {
  const { t, i18n } = useTranslation();
  // Helper function to get nested translation
  const translate = (key, options = {}) => {
    return t(key, options);
  };
  // Common translations shortcuts
  const common = {
    welcome: () => t('common.welcome'),
    save: () => t('common.save'),
    cancel: () => t('common.cancel'),
    delete: () => t('common.delete'),
    edit: () => t('common.edit'),
    submit: () => t('common.submit'),
    search: () => t('common.search'),
    loading: () => t('common.loading'),
    error: () => t('common.error'),
    success: () => t('common.success'),
  };
  const navigation = {
    dashboard: () => t('navigation.dashboard'),
    beneficiaries: () => t('navigation.beneficiaries'),
    programs: () => t('navigation.programs'),
    evaluations: () => t('navigation.evaluations'),
    calendar: () => t('navigation.calendar'),
    documents: () => t('navigation.documents'),
    reports: () => t('navigation.reports'),
    settings: () => t('navigation.settings'),
    users: () => t('navigation.users'),
    profile: () => t('navigation.profile'),
  };
  const auth = {
    loginTitle: () => t('auth.loginTitle'),
    email: () => t('auth.email'),
    password: () => t('auth.password'),
    signIn: () => t('auth.signIn'),
    signOut: () => t('auth.signOut'),
    loginError: () => t('auth.loginError'),
  };
  const errors = {
    generic: () => t('errors.generic'),
    network: () => t('errors.network'),
    notFound: () => t('errors.notFound'),
    unauthorized: () => t('errors.unauthorized'),
    validation: () => t('errors.validation'),
  };
  const success = {
    saved: () => t('success.saved'),
    created: () => t('success.created'),
    updated: () => t('success.updated'),
    deleted: () => t('success.deleted'),
  };
  return {
    t: translate,
    i18n,
    common,
    navigation,
    auth,
    errors,
    success,
  };
};
export default useTranslations;