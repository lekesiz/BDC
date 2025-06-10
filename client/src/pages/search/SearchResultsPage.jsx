import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  X, 
  ChevronLeft,
  ChevronRight,
  Calendar,
  Users,
  User,
  FileText,
  ClipboardList,
  TrendingUp,
  Download,
  SlidersHorizontal
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import api from '@/lib/api';
import { formatDate } from '@/lib/utils';

const SearchResultsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const initialQuery = searchParams.get('q') || '';
  const initialType = searchParams.get('type') || 'all';
  
  const [query, setQuery] = useState(initialQuery);
  const [activeType, setActiveType] = useState(initialType);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    date_range: { start: '', end: '' },
    status: 'all',
    include_inactive: false
  });
  
  // Entity type configurations
  const entityTypes = {
    all: { label: 'All', icon: Search },
    beneficiaries: { label: 'Beneficiaries', icon: Users },
    users: { label: 'Users', icon: User },
    appointments: { label: 'Appointments', icon: Calendar },
    documents: { label: 'Documents', icon: FileText },
    tests: { label: 'Evaluations', icon: ClipboardList },
    programs: { label: 'Programs', icon: TrendingUp }
  };

  // Perform search
  const performSearch = useCallback(async () => {
    if (!query || query.length < 2) {
      setResults(null);
      return;
    }

    setIsLoading(true);
    try {
      const params = {
        q: query,
        limit: 20,
        include_inactive: filters.include_inactive
      };
      
      if (activeType !== 'all') {
        params.types = activeType;
      }

      const response = await api.get('/api/v2/search/global', { params });
      setResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
      addToast({
        type: 'error',
        title: 'Search Failed',
        message: 'Unable to perform search. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  }, [query, activeType, filters, addToast]);

  // Search when params change
  useEffect(() => {
    performSearch();
  }, [performSearch]);

  // Update URL params
  const updateSearchParams = (newQuery, newType) => {
    const params = new URLSearchParams();
    if (newQuery) params.set('q', newQuery);
    if (newType && newType !== 'all') params.set('type', newType);
    setSearchParams(params);
  };

  // Handle search submit
  const handleSearch = (e) => {
    e.preventDefault();
    updateSearchParams(query, activeType);
  };

  // Handle type change
  const handleTypeChange = (type) => {
    setActiveType(type);
    updateSearchParams(query, type);
  };

  // Navigate to result
  const handleResultClick = (result) => {
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
    }
  };

  // Export results
  const handleExport = async (format = 'csv') => {
    try {
      const response = await api.post('/api/v2/search/export', {
        query,
        filters: {
          entity_type: activeType === 'all' ? null : activeType,
          ...filters
        },
        format
      });

      if (format === 'csv') {
        // Handle CSV download
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `search_results_${new Date().toISOString()}.csv`;
        link.click();
      }

      addToast({
        type: 'success',
        title: 'Export Successful',
        message: `Results exported as ${format.toUpperCase()}`
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Export Failed',
        message: 'Unable to export results'
      });
    }
  };

  // Get total results count
  const getTotalResults = () => {
    if (!results) return 0;
    return results.total_results || 0;
  };

  // Get results for current type
  const getFilteredResults = () => {
    if (!results || !results.results_by_type) return [];
    
    if (activeType === 'all') {
      // Flatten all results
      const allResults = [];
      Object.entries(results.results_by_type).forEach(([type, typeResults]) => {
        typeResults.results.forEach(result => {
          allResults.push({ ...result, type });
        });
      });
      return allResults;
    } else {
      // Return specific type results
      const typeResults = results.results_by_type[activeType];
      return typeResults ? typeResults.results.map(r => ({ ...r, type: activeType })) : [];
    }
  };

  const filteredResults = getFilteredResults();

  return (
    <div className="container mx-auto py-6 px-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Search Results</h1>
        <p className="text-gray-600">
          {getTotalResults() > 0 
            ? `Found ${getTotalResults()} results for "${query}"`
            : 'Enter a search term to find results'
          }
        </p>
      </div>

      {/* Search Bar */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search everything..."
                className="pl-10"
              />
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <SlidersHorizontal className="h-4 w-4 mr-2" />
              Filters
            </Button>
          </form>

          {/* Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Date Range</label>
                <div className="flex gap-2">
                  <Input
                    type="date"
                    value={filters.date_range.start}
                    onChange={(e) => setFilters({
                      ...filters,
                      date_range: { ...filters.date_range, start: e.target.value }
                    })}
                    className="text-sm"
                  />
                  <span className="self-center">to</span>
                  <Input
                    type="date"
                    value={filters.date_range.end}
                    onChange={(e) => setFilters({
                      ...filters,
                      date_range: { ...filters.date_range, end: e.target.value }
                    })}
                    className="text-sm"
                  />
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-1 block">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="all">All</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                </select>
              </div>

              <div className="flex items-end">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={filters.include_inactive}
                    onChange={(e) => setFilters({ ...filters, include_inactive: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Include inactive records</span>
                </label>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Type Filter Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Filter by Type</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="space-y-1">
                {Object.entries(entityTypes).map(([type, config]) => {
                  const Icon = config.icon;
                  const count = type === 'all' 
                    ? getTotalResults()
                    : results?.results_by_type[type]?.total || 0;
                  
                  return (
                    <button
                      key={type}
                      onClick={() => handleTypeChange(type)}
                      className={`w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50 transition-colors ${
                        activeType === type ? 'bg-primary/10 border-l-4 border-primary' : ''
                      }`}
                    >
                      <span className="flex items-center">
                        <Icon className="h-4 w-4 mr-3 text-gray-500" />
                        <span className="text-sm font-medium">{config.label}</span>
                      </span>
                      <Badge variant="secondary" className="text-xs">
                        {count}
                      </Badge>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results List */}
        <div className="lg:col-span-3">
          {isLoading ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="animate-pulse space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3 mx-auto"></div>
                </div>
              </CardContent>
            </Card>
          ) : filteredResults.length > 0 ? (
            <>
              {/* Results Actions */}
              <div className="flex justify-between items-center mb-4">
                <p className="text-sm text-gray-600">
                  Showing {filteredResults.length} results
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('csv')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>

              {/* Results Grid */}
              <div className="space-y-4">
                {filteredResults.map((result, index) => {
                  const Icon = entityTypes[result.type]?.icon || FileText;
                  
                  return (
                    <Card 
                      key={`${result.type}-${result.id}`}
                      className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => handleResultClick(result)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-4">
                            <div className="p-2 bg-gray-100 rounded-lg">
                              <Icon className="h-5 w-5 text-gray-600" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-medium text-lg">
                                {result.first_name && result.last_name
                                  ? `${result.first_name} ${result.last_name}`
                                  : result.name || result.title || 'Untitled'}
                              </h3>
                              <p className="text-sm text-gray-600 mt-1">
                                {result.email || result.description || ''}
                              </p>
                              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                <span className="flex items-center">
                                  Type: {entityTypes[result.type]?.label}
                                </span>
                                {result.created_at && (
                                  <span className="flex items-center">
                                    <Calendar className="h-3 w-3 mr-1" />
                                    {formatDate(result.created_at)}
                                  </span>
                                )}
                                {result.matched_fields && (
                                  <span>
                                    Matched in: {result.matched_fields.join(', ')}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {result.status && (
                            <Badge 
                              variant={
                                result.status === 'active' ? 'success' :
                                result.status === 'inactive' ? 'secondary' :
                                'warning'
                              }
                            >
                              {result.status}
                            </Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </>
          ) : query ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No results found</h3>
                <p className="text-gray-500">
                  Try adjusting your search terms or filters
                </p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Start searching</h3>
                <p className="text-gray-500">
                  Enter a search term to find beneficiaries, users, appointments, and more
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchResultsPage;