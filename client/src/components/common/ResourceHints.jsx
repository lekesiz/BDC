// TODO: i18n - processed
import { useEffect } from 'react';import { useTranslation } from "react-i18next";
const ResourceHints = ({
  preconnectUrls = [],
  prefetchUrls = [],
  preloadResources = [],
  dnsPrefetchUrls = []
}) => {const { t } = useTranslation();
  useEffect(() => {
    const head = document.head;
    // Add preconnect hints
    preconnectUrls.forEach((url) => {
      if (!document.querySelector(`link[rel="preconnect"][href="${url}"]`)) {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = url;
        link.crossOrigin = 'anonymous';
        head.appendChild(link);
      }
    });
    // Add DNS prefetch hints
    dnsPrefetchUrls.forEach((url) => {
      if (!document.querySelector(`link[rel="dns-prefetch"][href="${url}"]`)) {
        const link = document.createElement('link');
        link.rel = 'dns-prefetch';
        link.href = url;
        head.appendChild(link);
      }
    });
    // Add prefetch hints
    prefetchUrls.forEach((url) => {
      if (!document.querySelector(`link[rel="prefetch"][href="${url}"]`)) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        link.as = url.endsWith('.js') ? 'script' :
        url.endsWith('.css') ? 'style' :
        url.match(/\.(jpg|jpeg|png|webp|avif)$/i) ? 'image' : 'fetch';
        head.appendChild(link);
      }
    });
    // Add preload hints
    preloadResources.forEach(({ href, as, type, crossOrigin }) => {
      if (!document.querySelector(`link[rel="preload"][href="${href}"]`)) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        if (type) link.type = type;
        if (crossOrigin) link.crossOrigin = crossOrigin;
        head.appendChild(link);
      }
    });
    // Cleanup function
    return () => {
      // Only remove hints added by this component
      const selectors = [
      ...preconnectUrls.map((url) => `link[rel="preconnect"][href="${url}"]`),
      ...dnsPrefetchUrls.map((url) => `link[rel="dns-prefetch"][href="${url}"]`),
      ...prefetchUrls.map((url) => `link[rel="prefetch"][href="${url}"]`),
      ...preloadResources.map(({ href }) => `link[rel="preload"][href="${href}"]`)];

      selectors.forEach((selector) => {
        const element = document.querySelector(selector);
        if (element) {
          element.remove();
        }
      });
    };
  }, [preconnectUrls, prefetchUrls, preloadResources, dnsPrefetchUrls]);
  return null;
};
export default ResourceHints;