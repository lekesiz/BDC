// TODO: i18n - processed
/**
 * Lazy Loader
 * 
 * Advanced lazy loading for components, images, and resources.
 */

import React, { Suspense, lazy, useState, useEffect, useRef } from 'react';import { useTranslation } from "react-i18next";

class LazyLoader {
  constructor(config = {}) {
    this.config = {
      threshold: 0.1, // Intersection threshold
      rootMargin: '50px', // Load 50px before element is visible
      enableImageLazyLoading: true,
      enableComponentLazyLoading: true,
      enableResourceLazyLoading: true,
      retryAttempts: 3,
      retryDelay: 1000,
      preloadDistance: 2, // Preload components 2 screens away
      ...config
    };

    this.intersectionObserver = null;
    this.loadedComponents = new Set();
    this.loadingComponents = new Map();
    this.componentCache = new Map();
    this.imageCache = new Map();
    this.isInitialized = false;

    // Bind methods
    this.init = this.init.bind(this);
    this.wrapComponent = this.wrapComponent.bind(this);
    this.lazyLoadImage = this.lazyLoadImage.bind(this);
  }

  /**
   * Initialize lazy loader
   */
  init() {
    if (this.isInitialized) {
      return;
    }

    console.log('🔄 Initializing Lazy Loader...');

    // Initialize Intersection Observer for lazy loading
    this._initIntersectionObserver();

    // Initialize image lazy loading if enabled
    if (this.config.enableImageLazyLoading) {
      this._initImageLazyLoading();
    }

    // Initialize resource lazy loading if enabled
    if (this.config.enableResourceLazyLoading) {
      this._initResourceLazyLoading();
    }

    this.isInitialized = true;
    console.log('✅ Lazy Loader initialized');
  }

  /**
   * Wrap a component for lazy loading
   */
  wrapComponent(componentImport, fallback = null) {
    if (typeof componentImport === 'function') {
      // Dynamic import function
      const LazyComponent = lazy(() => this._loadComponentWithRetry(componentImport));

      return (props) =>
      <Suspense fallback={fallback || this._getDefaultFallback()}>
          <LazyComponent {...props} />
        </Suspense>;

    } else {
      // Already imported component
      return componentImport;
    }
  }

  /**
   * Create lazy-loaded image component
   */
  lazyLoadImage(src, options = {}) {
    const LazyImage = ({ alt, className, style, onLoad, onError, ...props }) => {const { t } = useTranslation();
      const [isLoaded, setIsLoaded] = useState(false);
      const [isInView, setIsInView] = useState(false);
      const [hasError, setHasError] = useState(false);
      const imgRef = useRef(null);
      const placeholderRef = useRef(null);

      useEffect(() => {
        const observer = new IntersectionObserver(
          ([entry]) => {
            if (entry.isIntersecting) {
              setIsInView(true);
              observer.disconnect();
            }
          },
          {
            threshold: this.config.threshold,
            rootMargin: this.config.rootMargin
          }
        );

        if (placeholderRef.current) {
          observer.observe(placeholderRef.current);
        }

        return () => observer.disconnect();
      }, []);

      useEffect(() => {
        if (isInView && !isLoaded && !hasError) {
          this._loadImage(src).
          then(() => {
            setIsLoaded(true);
            onLoad && onLoad();
          }).
          catch((error) => {
            setHasError(true);
            onError && onError(error);
          });
        }
      }, [isInView, isLoaded, hasError, src, onLoad, onError]);

      if (!isInView) {
        return (
          <div
            ref={placeholderRef}
            className={`lazy-image-placeholder ${className || ''}`}
            style={{
              backgroundColor: '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '200px',
              ...style
            }}
            {...props}>

            {options.placeholder || '🖼️'}
          </div>);

      }

      if (hasError) {
        return (
          <div
            className={`lazy-image-error ${className || ''}`}
            style={{
              backgroundColor: '#ffe6e6',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '200px',
              color: '#d32f2f',
              ...style
            }}
            {...props}>

            {options.errorFallback || '⚠️ Failed to load image'}
          </div>);

      }

      if (!isLoaded) {
        return (
          <div
            className={`lazy-image-loading ${className || ''}`}
            style={{
              backgroundColor: '#f5f5f5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '200px',
              ...style
            }}
            {...props}>

            {options.loadingIndicator || this._getLoadingSpinner()}
          </div>);

      }

      return (
        <img
          ref={imgRef}
          src={src}
          alt={alt}
          className={className}
          style={style}
          {...props} />);


    };

    return LazyImage;
  }

  /**
   * Lazy load a resource (CSS, JS, etc.)
   */
  lazyLoadResource(src, type = 'script') {
    return new Promise((resolve, reject) => {
      // Check if already loaded
      if (this._isResourceLoaded(src)) {
        resolve();
        return;
      }

      let element;

      if (type === 'script') {
        element = document.createElement('script');
        element.src = src;
        element.async = true;
      } else if (type === 'style') {
        element = document.createElement('link');
        element.rel = 'stylesheet';
        element.href = src;
      } else {
        reject(new Error(`Unsupported resource type: ${type}`));
        return;
      }

      element.onload = () => {
        console.log(`✅ Lazy loaded ${type}: ${src}`);
        resolve();
      };

      element.onerror = () => {
        console.error(`❌ Failed to lazy load ${type}: ${src}`);
        reject(new Error(`Failed to load ${src}`));
      };

      document.head.appendChild(element);
    });
  }

  /**
   * Preload components that are likely to be needed soon
   */
  preloadComponent(componentImport) {
    if (typeof componentImport === 'function') {
      return componentImport().catch((error) => {
        console.warn('Preload failed:', error);
      });
    }
    return Promise.resolve();
  }

  /**
   * Get lazy loading statistics
   */
  getStats() {
    return {
      loadedComponents: this.loadedComponents.size,
      cachedComponents: this.componentCache.size,
      cachedImages: this.imageCache.size,
      currentlyLoading: this.loadingComponents.size
    };
  }

  // Private methods

  _initIntersectionObserver() {
    if ('IntersectionObserver' in window) {
      this.intersectionObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              this._handleIntersection(entry.target);
            }
          });
        },
        {
          threshold: this.config.threshold,
          rootMargin: this.config.rootMargin
        }
      );
    } else {
      console.warn('IntersectionObserver not supported, falling back to immediate loading');
    }
  }

  _initImageLazyLoading() {
    // Find all images with data-lazy-src attribute
    const lazyImages = document.querySelectorAll('img[data-lazy-src]');

    lazyImages.forEach((img) => {
      if (this.intersectionObserver) {
        this.intersectionObserver.observe(img);
      } else {
        // Fallback for browsers without IntersectionObserver
        this._loadLazyImage(img);
      }
    });
  }

  _initResourceLazyLoading() {
    // Find all resources with data-lazy-load attribute
    const lazyResources = document.querySelectorAll('[data-lazy-load]');

    lazyResources.forEach((element) => {
      if (this.intersectionObserver) {
        this.intersectionObserver.observe(element);
      } else {
        // Fallback for browsers without IntersectionObserver
        this._loadLazyResource(element);
      }
    });
  }

  async _loadComponentWithRetry(componentImport) {
    const cacheKey = componentImport.toString();

    // Check cache first
    if (this.componentCache.has(cacheKey)) {
      return this.componentCache.get(cacheKey);
    }

    // Check if already loading
    if (this.loadingComponents.has(cacheKey)) {
      return this.loadingComponents.get(cacheKey);
    }

    const loadPromise = this._retryComponentLoad(componentImport);
    this.loadingComponents.set(cacheKey, loadPromise);

    try {
      const component = await loadPromise;
      this.componentCache.set(cacheKey, component);
      this.loadedComponents.add(cacheKey);
      this.loadingComponents.delete(cacheKey);
      return component;
    } catch (error) {
      this.loadingComponents.delete(cacheKey);
      throw error;
    }
  }

  async _retryComponentLoad(componentImport, attempt = 1) {
    try {
      const startTime = performance.now();
      const component = await componentImport();
      const loadTime = performance.now() - startTime;

      console.log(`✅ Component loaded in ${loadTime.toFixed(2)}ms (attempt ${attempt})`);
      return component;
    } catch (error) {
      console.warn(`⚠️ Component load failed (attempt ${attempt}):`, error);

      if (attempt < this.config.retryAttempts) {
        await this._delay(this.config.retryDelay * attempt);
        return this._retryComponentLoad(componentImport, attempt + 1);
      } else {
        console.error(`❌ Component load failed after ${this.config.retryAttempts} attempts`);
        throw error;
      }
    }
  }

  async _loadImage(src) {
    // Check cache first
    if (this.imageCache.has(src)) {
      return this.imageCache.get(src);
    }

    return new Promise((resolve, reject) => {
      const img = new Image();

      img.onload = () => {
        this.imageCache.set(src, img);
        resolve(img);
      };

      img.onerror = () => {
        reject(new Error(`Failed to load image: ${src}`));
      };

      img.src = src;
    });
  }

  _handleIntersection(target) {
    if (target.dataset.lazySrc) {
      this._loadLazyImage(target);
    } else if (target.dataset.lazyLoad) {
      this._loadLazyResource(target);
    }
  }

  _loadLazyImage(img) {
    const src = img.dataset.lazySrc;

    if (src) {
      this._loadImage(src).
      then(() => {
        img.src = src;
        img.classList.add('lazy-loaded');
        img.removeAttribute('data-lazy-src');

        if (this.intersectionObserver) {
          this.intersectionObserver.unobserve(img);
        }
      }).
      catch((error) => {
        console.error('Failed to load lazy image:', error);
        img.classList.add('lazy-error');
      });
    }
  }

  _loadLazyResource(element) {
    const resourceUrl = element.dataset.lazyLoad;
    const resourceType = element.dataset.lazyType || 'script';

    if (resourceUrl) {
      this.lazyLoadResource(resourceUrl, resourceType).
      then(() => {
        element.classList.add('lazy-loaded');
        element.removeAttribute('data-lazy-load');

        if (this.intersectionObserver) {
          this.intersectionObserver.unobserve(element);
        }
      }).
      catch((error) => {
        console.error('Failed to load lazy resource:', error);
        element.classList.add('lazy-error');
      });
    }
  }

  _isResourceLoaded(src) {
    // Check if script is already loaded
    const scripts = document.querySelectorAll('script[src]');
    for (let script of scripts) {
      if (script.src === src) {
        return true;
      }
    }

    // Check if stylesheet is already loaded
    const links = document.querySelectorAll('link[href]');
    for (let link of links) {
      if (link.href === src) {
        return true;
      }
    }

    return false;
  }

  _getDefaultFallback() {
    return (
      <div className="lazy-component-loading">
        {this._getLoadingSpinner()}
        <span>Loading component...</span>
      </div>);

  }

  _getLoadingSpinner() {
    return (
      <div className="loading-spinner">
        <div className="spinner-circle"></div>
      </div>);

  }

  _delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export default LazyLoader;