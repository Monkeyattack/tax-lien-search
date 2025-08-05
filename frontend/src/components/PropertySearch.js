import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import api from '../services/authService';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  HomeIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  StarIcon,
  MapPinIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

const PropertySearch = ({ onPropertySelect }) => {
  const [searchText, setSearchText] = useState('');
  const [showFilters, setShowFilters] = useState(false);
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

  // Search properties
  const { data: properties, isLoading, refetch } = useQuery(
    ['propertySearch', filters, searchText],
    () => api.post('/property-search/search', {
      ...filters,
      search_text: searchText,
    }).then(res => res.data),
    { keepPreviousData: true }
  );

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
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
      <div className="flex gap-2">
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
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-secondary inline-flex items-center ${showFilters ? 'bg-tax-primary text-white' : ''}`}
        >
          <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
          Filters
        </button>
      </div>

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
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tax-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching properties...</p>
          </div>
        ) : properties && properties.length > 0 ? (
          properties.map((property) => (
            <div
              key={property.id}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => onPropertySelect && onPropertySelect(property)}
            >
              <div className="card-body">
                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
                  {/* Property Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {property.property_address}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {property.city}, {property.state} {property.zip_code}
                        </p>
                      </div>
                      {property.investment_score && (
                        <div className={`text-2xl font-bold ${getScoreColor(property.investment_score)}`}>
                          {Math.round(property.investment_score)}
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      {/* Property Details */}
                      <div>
                        <p className="text-xs text-gray-500">Property Type</p>
                        <p className="font-medium">{property.property_type || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Owner</p>
                        <p className="font-medium truncate">{property.owner_name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Parcel #</p>
                        <p className="font-medium">{property.parcel_number}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">County</p>
                        <p className="font-medium">{property.county_name}</p>
                      </div>

                      {/* Property Specs */}
                      {property.bedrooms && (
                        <div>
                          <p className="text-xs text-gray-500">Beds/Baths</p>
                          <p className="font-medium">
                            {property.bedrooms} / {property.bathrooms || '?'}
                          </p>
                        </div>
                      )}
                      {property.square_footage && (
                        <div>
                          <p className="text-xs text-gray-500">Sq Ft</p>
                          <p className="font-medium">{property.square_footage.toLocaleString()}</p>
                        </div>
                      )}
                      {property.year_built && (
                        <div>
                          <p className="text-xs text-gray-500">Year Built</p>
                          <p className="font-medium">{property.year_built}</p>
                        </div>
                      )}
                      {property.lot_size_sqft && (
                        <div>
                          <p className="text-xs text-gray-500">Lot Size</p>
                          <p className="font-medium">{property.lot_size_sqft.toLocaleString()} sqft</p>
                        </div>
                      )}

                      {/* Values */}
                      <div>
                        <p className="text-xs text-gray-500">Assessed Value</p>
                        <p className="font-medium">{formatCurrency(property.assessed_value)}</p>
                      </div>
                      {property.zestimate && (
                        <div>
                          <p className="text-xs text-gray-500">Zestimate®</p>
                          <p className="font-medium">{formatCurrency(property.zestimate)}</p>
                        </div>
                      )}
                      {property.monthly_rent_estimate && (
                        <div>
                          <p className="text-xs text-gray-500">Est. Rent</p>
                          <p className="font-medium">{formatCurrency(property.monthly_rent_estimate)}/mo</p>
                        </div>
                      )}
                      {property.roi_percentage && (
                        <div>
                          <p className="text-xs text-gray-500">Est. ROI</p>
                          <p className="font-medium text-green-600">{property.roi_percentage.toFixed(1)}%</p>
                        </div>
                      )}
                    </div>

                    {/* Tax Sale Info */}
                    {property.next_sale_date && (
                      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <CalendarIcon className="h-5 w-5 text-yellow-600 mr-2" />
                            <div>
                              <p className="text-sm font-medium text-yellow-800">
                                Tax Sale: {new Date(property.next_sale_date).toLocaleDateString()}
                              </p>
                              <p className="text-xs text-yellow-600">
                                Minimum Bid: {formatCurrency(property.minimum_bid)} | 
                                Taxes Owed: {formatCurrency(property.taxes_owed)}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Neighborhood Info */}
                    <div className="mt-3 flex gap-4 text-sm text-gray-600">
                      {property.school_rating && (
                        <div className="flex items-center">
                          <StarIcon className="h-4 w-4 mr-1" />
                          School Rating: {property.school_rating.toFixed(1)}/10
                        </div>
                      )}
                      {property.walk_score && (
                        <div className="flex items-center">
                          <MapPinIcon className="h-4 w-4 mr-1" />
                          Walk Score: {property.walk_score}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <HomeIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No properties found matching your criteria</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PropertySearch;