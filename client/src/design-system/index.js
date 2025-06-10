// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Design System Main Export
export * from './tokens';
export * from './components';
export * from './animations';
export * from './accessibility';
export * from './themes';
export * from './states';
export * from './utils';

// Main provider
export { DesignSystemProvider } from './DesignSystemProvider';

// Hooks
export { useTheme } from './hooks/useTheme';
export { useAnimation } from './hooks/useAnimation';
export { useAccessibility } from './hooks/useAccessibility';
export { useBreakpoint } from './hooks/useBreakpoint';
export { useDesignSystem } from './hooks/useDesignSystem';