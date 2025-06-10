// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Z-Index System
export const zIndex = {
  // Base layers
  base: 0,
  below: -1,

  // Content layers
  content: 1,
  elevated: 10,
  sticky: 100,
  fixed: 200,

  // Overlay layers
  dropdown: 1000,
  overlay: 1100,
  modal: 1200,
  popover: 1300,
  tooltip: 1400,
  notification: 1500,

  // Top layers
  max: 9999,

  // Component-specific
  component: {
    header: 100,
    sidebar: 150,
    mobileNav: 200,
    backdrop: 1000,
    dialog: 1200,
    toast: 1500,
    debugPanel: 9999
  }
};