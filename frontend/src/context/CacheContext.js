import React, { createContext, useContext, useState, useEffect } from 'react';

const CacheContext = createContext();

// Cache duration in milliseconds (e.g., 5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

export function CacheProvider({ children }) {
  const [cache, setCache] = useState(() => {
    // Load cache from localStorage on initial render
    const savedCache = localStorage.getItem('stockCache');
    return savedCache ? JSON.parse(savedCache) : {};
  });

  // Save cache to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('stockCache', JSON.stringify(cache));
  }, [cache]);

  const getCachedData = (key) => {
    const cachedItem = cache[key];
    if (!cachedItem) return null;

    // Check if cache has expired
    if (Date.now() - cachedItem.timestamp > CACHE_DURATION) {
      // Remove expired cache
      const newCache = { ...cache };
      delete newCache[key];
      setCache(newCache);
      return null;
    }

    return cachedItem.data;
  };

  const setCachedData = (key, data) => {
    setCache(prevCache => ({
      ...prevCache,
      [key]: {
        data,
        timestamp: Date.now()
      }
    }));
  };

  return (
    <CacheContext.Provider value={{ getCachedData, setCachedData }}>
      {children}
    </CacheContext.Provider>
  );
};

export function useCache() {
  return useContext(CacheContext);
} 