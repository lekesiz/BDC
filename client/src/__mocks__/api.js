// TODO: i18n - processed
import { vi } from 'vitest';import { useTranslation } from "react-i18next";
const api = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() }
  },
  defaults: {
    headers: {
      common: {}
    }
  }
};
export default api;