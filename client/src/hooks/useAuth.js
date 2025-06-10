// TODO: i18n - processed
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
/**
 * Custom hook to use the authentication context
 * 
 * @returns {Object} Authentication context
 */import { useTranslation } from "react-i18next";
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};