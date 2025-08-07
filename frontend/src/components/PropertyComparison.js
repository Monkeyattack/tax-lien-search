import React, { useState } from 'react';
import {
  XMarkIcon,
  ArrowsUpDownIcon,
  HomeIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  StarIcon,
  MapPinIcon,
  PrinterIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

const PropertyComparison = ({ properties, onClose, onRemoveProperty }) => {
  const [sortField, setSortField] = useState('investment_score');
  const [sortOrder, setSortOrder] = useState('desc');

  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (date) => {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString();
  };

  const getScoreColor = (score) => {
    if (!score) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getBestValue = (properties, field, isHigherBetter = true) => {
    const values = properties.map(p => p[field]).filter(v => v != null && v !== '');
    if (values.length === 0) return null;
    return isHigherBetter ? Math.max(...values) : Math.min(...values);
  };

  const isBestValue = (value, bestValue) => {
    return value === bestValue && value != null && value !== '';
  };

  const sortedProperties = [...properties].sort((a, b) => {
    const aValue = a[sortField] || 0;
    const bValue = b[sortField] || 0;
    return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
  });

  const comparisonFields = [
    { key: 'investment_score', label: 'Investment Score', type: 'score', higherBetter: true },
    { key: 'roi_percentage', label: 'ROI %', type: 'percentage', higherBetter: true },
    { key: 'assessed_value', label: 'Assessed Value', type: 'currency', higherBetter: true },
    { key: 'zestimate', label: 'Zestimate®', type: 'currency', higherBetter: true },
    { key: 'minimum_bid', label: 'Minimum Bid', type: 'currency', higherBetter: false },
    { key: 'taxes_owed', label: 'Taxes Owed', type: 'currency', higherBetter: false },
    { key: 'monthly_rent_estimate', label: 'Est. Rent', type: 'currency', higherBetter: true },
    { key: 'next_sale_date', label: 'Sale Date', type: 'date', higherBetter: false },
    { key: 'square_footage', label: 'Square Feet', type: 'number', higherBetter: true },
    { key: 'year_built', label: 'Year Built', type: 'number', higherBetter: true },
    { key: 'school_rating', label: 'School Rating', type: 'decimal', higherBetter: true },
    { key: 'walk_score', label: 'Walk Score', type: 'number', higherBetter: true },
  ];

  const formatValue = (value, type) => {
    if (!value && value !== 0) return 'N/A';
    
    switch (type) {
      case 'currency':
        return formatCurrency(value);
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'date':
        return formatDate(value);
      case 'decimal':
        return value.toFixed(1);
      case 'score':
        return Math.round(value);
      case 'number':
        return value.toLocaleString();
      default:
        return value;
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (properties.length === 0) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 print:hidden">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Property Comparison ({properties.length})
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Compare properties side by side to make informed investment decisions
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <ArrowsUpDownIcon className="h-4 w-4 text-gray-400" />
              <select
                value={sortField}
                onChange={(e) => setSortField(e.target.value)}
                className="text-sm border-gray-300 rounded-md"
              >
                <option value="investment_score">Investment Score</option>
                <option value="roi_percentage">ROI</option>
                <option value="assessed_value">Assessed Value</option>
                <option value="minimum_bid">Minimum Bid</option>
                <option value="next_sale_date">Sale Date</option>
              </select>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
                className="text-sm border-gray-300 rounded-md"
              >
                <option value="desc">High to Low</option>
                <option value="asc">Low to High</option>
              </select>
            </div>
            <button
              onClick={handlePrint}
              className="btn-secondary inline-flex items-center text-sm"
            >
              <PrinterIcon className="h-4 w-4 mr-2" />
              Print
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Comparison Table */}
        <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Property
                  </th>
                  {sortedProperties.map((property, index) => (
                    <th key={property.id} className="px-4 py-3 text-left min-w-[200px]">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-semibold text-gray-900 truncate">
                            {property.property_address || 'Address Not Available'}
                          </h3>
                          <div className="flex items-center mt-1 text-xs text-gray-500">
                            <MapPinIcon className="h-3 w-3 mr-1" />
                            <span className="truncate">
                              {property.city ? `${property.city}, ` : ''}
                              {property.state || 'TX'}
                            </span>
                          </div>
                          {property.investment_score && (
                            <div className={`mt-2 inline-flex px-2 py-1 text-xs font-bold rounded-full ${getScoreColor(property.investment_score)} bg-gray-100`}>
                              Score: {Math.round(property.investment_score)}
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => onRemoveProperty(property)}
                          className="ml-2 text-gray-400 hover:text-gray-600 print:hidden"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {comparisonFields.map((field) => {
                  const bestValue = getBestValue(sortedProperties, field.key, field.higherBetter);
                  
                  return (
                    <tr key={field.key} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                        {field.label}
                      </td>
                      {sortedProperties.map((property) => {
                        const value = property[field.key];
                        const isBest = isBestValue(value, bestValue);
                        
                        return (
                          <td
                            key={`${property.id}-${field.key}`}
                            className={`px-4 py-3 text-sm ${
                              isBest ? 'bg-green-50 text-green-800 font-semibold' : 'text-gray-900'
                            }`}
                          >
                            <div className="flex items-center">
                              {isBest && (
                                <StarIcon className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" />
                              )}
                              {formatValue(value, field.type)}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}

                {/* Additional Property Details */}
                <tr className="bg-gray-100">
                  <td className="px-4 py-3 text-sm font-semibold text-gray-900" colSpan={sortedProperties.length + 1}>
                    Property Details
                  </td>
                </tr>
                
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">Owner</td>
                  {sortedProperties.map((property) => (
                    <td key={`${property.id}-owner`} className="px-4 py-3 text-sm text-gray-900">
                      <div className="truncate" title={property.owner_name}>
                        {property.owner_name || 'N/A'}
                      </div>
                    </td>
                  ))}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">Parcel Number</td>
                  {sortedProperties.map((property) => (
                    <td key={`${property.id}-parcel`} className="px-4 py-3 text-sm text-gray-900 font-mono">
                      <div className="truncate" title={property.parcel_number}>
                        {property.parcel_number || 'N/A'}
                      </div>
                    </td>
                  ))}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">Property Type</td>
                  {sortedProperties.map((property) => (
                    <td key={`${property.id}-type`} className="px-4 py-3 text-sm text-gray-900">
                      {property.property_type || 'N/A'}
                    </td>
                  ))}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">County</td>
                  {sortedProperties.map((property) => (
                    <td key={`${property.id}-county`} className="px-4 py-3 text-sm text-gray-900">
                      {property.county_name || 'N/A'}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-between items-center print:hidden">
          <div className="text-sm text-gray-600">
            <StarIcon className="h-4 w-4 inline text-green-600 mr-1" />
            Best values are highlighted in green
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => {
                properties.forEach(onRemoveProperty);
              }}
              className="btn-secondary text-sm"
            >
              Clear All
            </button>
            <button
              onClick={onClose}
              className="btn-primary text-sm"
            >
              Close Comparison
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyComparison;