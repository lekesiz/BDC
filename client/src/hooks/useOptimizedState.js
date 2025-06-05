import { useState, useCallback, useRef, useMemo } from 'react';

/**
 * Optimized state hook that prevents unnecessary re-renders
 * Only updates when value actually changes
 */
export const useOptimizedState = (initialValue) => {
  const [value, setValue] = useState(initialValue);
  const valueRef = useRef(value);

  const setOptimizedValue = useCallback((newValue) => {
    const resolvedValue = typeof newValue === 'function' 
      ? newValue(valueRef.current) 
      : newValue;

    // Only update if value actually changed
    if (resolvedValue !== valueRef.current) {
      valueRef.current = resolvedValue;
      setValue(resolvedValue);
    }
  }, []);

  return [value, setOptimizedValue];
};

/**
 * Hook for expensive computations with memoization
 */
export const useComputedValue = (computeFn, dependencies = []) => {
  return useMemo(() => computeFn(), dependencies);
};

/**
 * Hook for optimized object state
 * Prevents re-renders when object reference changes but content is same
 */
export const useOptimizedObjectState = (initialValue = {}) => {
  const [value, setValue] = useState(initialValue);
  const valueRef = useRef(value);

  const setOptimizedValue = useCallback((newValue) => {
    const resolvedValue = typeof newValue === 'function' 
      ? newValue(valueRef.current) 
      : newValue;

    // Deep comparison for objects
    const hasChanged = JSON.stringify(resolvedValue) !== JSON.stringify(valueRef.current);
    
    if (hasChanged) {
      valueRef.current = resolvedValue;
      setValue(resolvedValue);
    }
  }, []);

  // Memoized update functions
  const updateField = useCallback((field, value) => {
    setOptimizedValue(prev => ({
      ...prev,
      [field]: value
    }));
  }, [setOptimizedValue]);

  const updateFields = useCallback((updates) => {
    setOptimizedValue(prev => ({
      ...prev,
      ...updates
    }));
  }, [setOptimizedValue]);

  return {
    value,
    setValue: setOptimizedValue,
    updateField,
    updateFields
  };
};

/**
 * Hook for optimized array state with common operations
 */
export const useOptimizedArrayState = (initialValue = []) => {
  const [items, setItems] = useState(initialValue);

  // Memoized operations
  const add = useCallback((item) => {
    setItems(prev => [...prev, item]);
  }, []);

  const remove = useCallback((predicate) => {
    setItems(prev => prev.filter(item => !predicate(item)));
  }, []);

  const update = useCallback((predicate, updates) => {
    setItems(prev => prev.map(item => 
      predicate(item) ? { ...item, ...updates } : item
    ));
  }, []);

  const clear = useCallback(() => {
    setItems([]);
  }, []);

  const replace = useCallback((newItems) => {
    setItems(newItems);
  }, []);

  return {
    items,
    add,
    remove,
    update,
    clear,
    replace
  };
};