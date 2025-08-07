import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import api from '../services/authService';
import SaveSearchModal from './SaveSearchModal';
import PropertyCard from './PropertyCard';
import PropertyComparison from './PropertyComparison';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  HomeIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  StarIcon,
  MapPinIcon,
  ChevronDownIcon,
  BookmarkIcon,
  ScaleIcon,
  ViewColumnsIcon,
  Squares2X2Icon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

const PropertySearch = ({ onPropertySelect }) => {
  const [searchText, setSearchText] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [selectedForComparison, setSelectedForComparison] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filters, setFilters] = useState({
    county_ids: [],
    cities: [],
    property_types: [],
    min_assessed_value: '',
    max_assessed_value: '',
    min_investment_score: '',
    min_roi_percentage: '',
    has_upcoming_sale: false,
    sort_by: 'investment_score',
    sort_order: 'desc',
  });

  // Fetch filter options
  const { data: filterOptions } = useQuery(
    'propertyFilters',
    () => api.get('/property-search/filters').then(res => res.data),
    { staleTime: 300000 } // 5 minutes
  );

  // Search properties - using simplified endpoint temporarily
  const { data: properties, isLoading, refetch } = useQuery(
    ['propertySearch', filters, searchText, 'v2'], // Added v2 to force cache refresh
    () => {
      // Use simplified endpoint for now
      return api.get(`/property-search/simple?limit=50&v=${Date.now()}`).then(res => res.data);
    },
    { keepPreviousData: true }
  );

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handlePropertySelect = (property) => {
    if (onPropertySelect) {
      onPropertySelect(property);
    }
  };

  const toggleComparisonSelect = (property) => {
    setSelectedForComparison(prev => {
      const exists = prev.find(p => p.id === property.id);
      if (exists) {
        return prev.filter(p => p.id !== property.id);
      } else {
        return [...prev, property].slice(0, 4); // Max 4 properties
      }
    });
  };

  const removeFromComparison = (propertyId) => {
    setSelectedForComparison(prev => prev.filter(p => p.id !== propertyId));
  };

  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getScoreColor = (score) => {
    if (!score) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="flex-1 relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by address, owner, parcel number..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-tax-primary focus:border-transparent"
          />
        </div>
        
        <div className="flex gap-2">
          {/* View Mode Toggle */}
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                viewMode === 'grid' 
                  ? 'bg-tax-primary text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
              title="Grid view"
            >
              <Squares2X2Icon className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 text-sm font-medium transition-colors border-l border-gray-300 ${
                viewMode === 'list' 
                  ? 'bg-tax-primary text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
              title="List view"
            >
              <ViewColumnsIcon className="h-4 w-4" />
            </button>
          </div>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary inline-flex items-center ${showFilters ? 'bg-tax-primary text-white' : ''}`}
          >
            <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
            Filters
          </button>
          
          <button
            onClick={() => setShowSaveModal(true)}
            className="btn-secondary inline-flex items-center"
            title="Save this search"
          >
            <BookmarkIcon className="h-5 w-5 mr-2" />
            Save
          </button>
        </div>
      </div>

      {/* Comparison Bar */}
      {selectedForComparison.length > 0 && (
        <div className="bg-tax-primary text-white rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <ScaleIcon className="h-5 w-5 mr-3" />
              <span className="font-medium">
                {selectedForComparison.length} properties selected for comparison
              </span>
              <span className="ml-2 text-sm opacity-90">
                (Max: 4 properties)
              </span>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowComparison(true)}
                disabled={selectedForComparison.length < 2}
                className="px-4 py-2 bg-white text-tax-primary rounded-md font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Compare Properties
              </button>
              <button
                onClick={() => setSelectedForComparison([])}
                className="px-3 py-2 text-white hover:bg-white hover:bg-opacity-20 rounded-md transition-colors"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Filters Panel */}
      {showFilters && filterOptions && (
        <div className="card">
          <div className="card-body">
            <h3 className="font-semibold mb-4">Search Filters</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* County Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  County
                </label>
                <select
                  multiple
                  value={filters.county_ids}
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                    handleFilterChange('county_ids', selected);
                  }}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                >
                  {filterOptions.counties.map(county => (
                    <option key={county.id} value={county.id}>
                      {county.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Property Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Property Type
                </label>
                <select
                  multiple
                  value={filters.property_types}
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => option.value);
                    handleFilterChange('property_types', selected);
                  }}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                >
                  {filterOptions.property_types.map(type => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              {/* Value Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Assessed Value Range
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.min_assessed_value}
                    onChange={(e) => handleFilterChange('min_assessed_value', e.target.value)}
                    className="w-1/2 border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.max_assessed_value}
                    onChange={(e) => handleFilterChange('max_assessed_value', e.target.value)}
                    className="w-1/2 border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                  />
                </div>
              </div>

              {/* Investment Score */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Investment Score
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={filters.min_investment_score}
                  onChange={(e) => handleFilterChange('min_investment_score', e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                />
              </div>

              {/* ROI */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min ROI %
                </label>
                <input
                  type="number"
                  min="0"
                  value={filters.min_roi_percentage}
                  onChange={(e) => handleFilterChange('min_roi_percentage', e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                />
              </div>

              {/* Upcoming Sale */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="has_upcoming_sale"
                  checked={filters.has_upcoming_sale}
                  onChange={(e) => handleFilterChange('has_upcoming_sale', e.target.checked)}
                  className="h-4 w-4 text-tax-primary focus:ring-tax-primary border-gray-300 rounded"
                />
                <label htmlFor="has_upcoming_sale" className="ml-2 text-sm text-gray-700">
                  Has Upcoming Sale Only
                </label>
              </div>
            </div>

            {/* Sort Options */}
            <div className="mt-4 flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <select
                  value={filters.sort_by}
                  onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                >
                  <option value="investment_score">Investment Score</option>
                  <option value="roi_percentage">ROI %</option>
                  <option value="minimum_bid">Minimum Bid</option>
                  <option value="sale_date">Sale Date</option>
                  <option value="assessed_value">Assessed Value</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order
                </label>
                <select
                  value={filters.sort_order}
                  onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-tax-primary focus:border-tax-primary"
                >
                  <option value="desc">High to Low</option>
                  <option value="asc">Low to High</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}


      {/* Results */}
      <div>
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tax-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching properties...</p>
          </div>
        ) : properties && properties.length > 0 ? (
          <>
            {/* Results Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  {properties.length} properties found
                </p>
                {selectedForComparison.length > 0 && (
                  <p className="text-sm text-tax-primary font-medium">
                    {selectedForComparison.length} selected for comparison
                  </p>
                )}
              </div>
            </div>

            {/* Grid/List View */}
            <div className={viewMode === 'grid' 
              ? "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" 
              : "space-y-4"
            }>
              {properties.map((property) => {
                const isSelected = selectedForComparison.find(p => p.id === property.id);
                
                return (
                  <div key={property.id} className="relative">
                    {/* Selection Checkbox for Comparison - moved to top right */}
                    <div className="absolute top-4 right-4 z-10">
                      <input
                        type="checkbox"
                        checked={!!isSelected}
                        onChange={(e) => {
                          e.stopPropagation();
                          toggleComparisonSelect(property);
                        }}
                        className="h-5 w-5 text-tax-primary focus:ring-tax-primary border-gray-300 rounded shadow-sm bg-white cursor-pointer"
                        title="Select for comparison"
                      />
                    </div>

                    <PropertyCard
                      property={property}
                      onSelect={handlePropertySelect}
                      className={`${isSelected ? 'ring-2 ring-tax-primary' : ''} ${
                        viewMode === 'list' ? 'max-w-none' : ''
                      }`}
                    />
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <HomeIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No properties found</h3>
            <p className="text-sm">Try adjusting your search criteria or filters</p>
          </div>
        )}
      </div>
      
      {/* Save Search Modal */}
      <SaveSearchModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        filters={{
          ...filters,
          search_text: searchText,
          // Convert empty strings to null for the API
          min_assessed_value: filters.min_assessed_value || null,
          max_assessed_value: filters.max_assessed_value || null,
          min_investment_score: filters.min_investment_score || null,
          min_roi_percentage: filters.min_roi_percentage || null,
        }}
      />

      {/* Property Comparison Modal */}
      {showComparison && (
        <PropertyComparison
          properties={selectedForComparison}
          onRemoveProperty={removeFromComparison}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
};

export default PropertySearch;