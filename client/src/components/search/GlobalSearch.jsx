import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  X, 
  User, 
  Users, 
  Calendar, 
  FileText, 
  ClipboardList,
  Loader2,
  ArrowRight,
  Filter,
  Clock,
  TrendingUp
} from 'lucide-react';
import { useDebounce } from '@/hooks/useDebounce';
import api from '@/lib/api';
import { cn } from '@/lib/utils';

const GlobalSearch = ({ className }) => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [recentSearches, setRecentSearches] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const searchRef = useRef(null);
  const inputRef = useRef(null);
  const debouncedQuery = useDebounce(query, 300);

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('bdc_recent_searches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  // Perform search when query changes
  useEffect(() => {
    if (debouncedQuery && debouncedQuery.length >= 2) {
      performSearch(debouncedQuery);
    } else {
      setResults(null);
    }
  }, [debouncedQuery]);

  // Handle clicks outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen || !results) return;

      const totalResults = getTotalResultsCount();
      
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => (prev + 1) % totalResults);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => prev <= 0 ? totalResults - 1 : prev - 1);
          break;
        case 'Enter':
          e.preventDefault();
          if (selectedIndex >= 0) {
            handleResultClick(getResultByIndex(selectedIndex));
          }
          break;
        case 'Escape':
          setIsOpen(false);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex]);

  const performSearch = async (searchQuery) => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/v2/search/global', {
        params: { q: searchQuery, limit: 5 }
      });
      setResults(response.data);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('Search failed:', error);
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResultClick = (result) => {
    // Save to recent searches
    saveRecentSearch(query);
    
    // Navigate based on result type
    const routes = {
      beneficiaries: `/beneficiaries/${result.id}`,
      users: `/users/${result.id}`,
      appointments: `/appointments/${result.id}`,
      documents: `/documents/${result.id}`,
      tests: `/evaluations/${result.id}`,
      programs: `/programs/${result.id}`
    };
    
    const route = routes[result.type];
    if (route) {
      navigate(route);
      setIsOpen(false);
      setQuery('');
    }
  };

  const saveRecentSearch = (searchQuery) => {
    const updated = [searchQuery, ...recentSearches.filter(s => s !== searchQuery)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('bdc_recent_searches', JSON.stringify(updated));
  };

  const getTotalResultsCount = () => {
    if (!results || !results.results_by_type) return 0;
    return Object.values(results.results_by_type).reduce(
      (total, typeResults) => total + typeResults.results.length, 0
    );
  };

  const getResultByIndex = (index) => {
    if (!results || !results.results_by_type) return null;
    
    let currentIndex = 0;
    for (const [type, typeResults] of Object.entries(results.results_by_type)) {
      for (const result of typeResults.results) {
        if (currentIndex === index) {
          return { ...result, type };
        }
        currentIndex++;
      }
    }
    return null;
  };

  const getResultIndex = (result, type) => {
    if (!results || !results.results_by_type) return -1;
    
    let currentIndex = 0;
    for (const [t, typeResults] of Object.entries(results.results_by_type)) {
      if (t === type) {
        const idx = typeResults.results.findIndex(r => r.id === result.id);
        if (idx !== -1) return currentIndex + idx;
      }
      currentIndex += typeResults.results.length;
    }
    return -1;
  };

  const getIcon = (type) => {
    const icons = {
      beneficiaries: Users,
      users: User,
      appointments: Calendar,
      documents: FileText,
      tests: ClipboardList,
      programs: TrendingUp
    };
    return icons[type] || FileText;
  };

  const getTypeLabel = (type) => {
    const labels = {
      beneficiaries: 'Beneficiaries',
      users: 'Users',
      appointments: 'Appointments',
      documents: 'Documents',
      tests: 'Evaluations',
      programs: 'Programs'
    };
    return labels[type] || type;
  };

  const highlightMatch = (text, query) => {
    if (!text || !query) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={index} className="bg-yellow-200 text-black">{part}</mark> : 
        part
    );
  };

  return (
    <div ref={searchRef} className={cn("relative", className)}>
      {/* Search Input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          placeholder="Search everything..."
          className={cn(
            "w-full pl-10 pr-4 py-2 rounded-lg border",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
            "transition-all duration-200",
            isOpen && "rounded-b-none"
          )}
        />
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="absolute right-3 top-1/2 -translate-y-1/2"
          >
            <X className="h-4 w-4 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 z-50 bg-white border border-t-0 rounded-b-lg shadow-lg max-h-[70vh] overflow-auto">
          {/* Loading State */}
          {isLoading && (
            <div className="p-8 text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="mt-2 text-sm text-gray-500">Searching...</p>
            </div>
          )}

          {/* No Query State - Show Recent Searches */}
          {!query && !isLoading && recentSearches.length > 0 && (
            <div className="p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                <Clock className="h-4 w-4 mr-2" />
                Recent Searches
              </h3>
              <div className="space-y-1">
                {recentSearches.map((search, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuery(search)}
                    className="w-full text-left px-3 py-2 text-sm rounded hover:bg-gray-100"
                  >
                    {search}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {!isLoading && results && results.total_results > 0 && (
            <div className="py-2">
              {Object.entries(results.results_by_type).map(([type, typeResults]) => {
                const Icon = getIcon(type);
                
                return (
                  <div key={type} className="mb-4">
                    <div className="px-4 py-2 bg-gray-50 border-y">
                      <h3 className="text-sm font-medium text-gray-700 flex items-center justify-between">
                        <span className="flex items-center">
                          <Icon className="h-4 w-4 mr-2" />
                          {getTypeLabel(type)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {typeResults.total} results
                        </span>
                      </h3>
                    </div>
                    
                    <div className="divide-y">
                      {typeResults.results.map((result) => {
                        const resultIndex = getResultIndex(result, type);
                        const isSelected = selectedIndex === resultIndex;
                        
                        return (
                          <button
                            key={result.id}
                            onClick={() => handleResultClick({ ...result, type })}
                            className={cn(
                              "w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors",
                              isSelected && "bg-primary/10"
                            )}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <div className="flex items-center">
                                  <span className="font-medium text-sm">
                                    {result.first_name && result.last_name
                                      ? highlightMatch(`${result.first_name} ${result.last_name}`, query)
                                      : result.name 
                                      ? highlightMatch(result.name, query)
                                      : result.title
                                      ? highlightMatch(result.title, query)
                                      : 'Untitled'}
                                  </span>
                                  {result.status && (
                                    <span className={cn(
                                      "ml-2 px-2 py-0.5 text-xs rounded-full",
                                      result.status === 'active' ? "bg-green-100 text-green-800" :
                                      result.status === 'inactive' ? "bg-gray-100 text-gray-800" :
                                      "bg-yellow-100 text-yellow-800"
                                    )}>
                                      {result.status}
                                    </span>
                                  )}
                                </div>
                                <div className="text-xs text-gray-500 mt-1">
                                  {result.email && highlightMatch(result.email, query)}
                                  {result.matched_fields && result.matched_fields.length > 0 && (
                                    <span className="ml-2">
                                      Matched in: {result.matched_fields.join(', ')}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <ArrowRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                            </div>
                          </button>
                        );
                      })}
                    </div>
                    
                    {typeResults.total > typeResults.results.length && (
                      <button
                        onClick={() => {
                          navigate(`/search?q=${encodeURIComponent(query)}&type=${type}`);
                          setIsOpen(false);
                        }}
                        className="w-full px-4 py-2 text-sm text-primary hover:bg-gray-50"
                      >
                        View all {typeResults.total} {getTypeLabel(type).toLowerCase()}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* No Results */}
          {!isLoading && results && results.total_results === 0 && (
            <div className="p-8 text-center">
              <Search className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No results found for "{query}"</p>
              <p className="text-sm text-gray-400 mt-1">Try a different search term</p>
            </div>
          )}

          {/* Footer Actions */}
          {query && (
            <div className="p-3 border-t bg-gray-50 flex items-center justify-between">
              <button
                onClick={() => {
                  navigate(`/search?q=${encodeURIComponent(query)}`);
                  setIsOpen(false);
                }}
                className="text-sm text-primary hover:underline flex items-center"
              >
                View all results
                <ArrowRight className="h-3 w-3 ml-1" />
              </button>
              
              <button
                onClick={() => setShowAdvanced(true)}
                className="text-sm text-gray-600 hover:text-gray-800 flex items-center"
              >
                <Filter className="h-3 w-3 mr-1" />
                Advanced Search
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GlobalSearch;