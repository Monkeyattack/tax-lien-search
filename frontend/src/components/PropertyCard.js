import React from 'react';
import {
  HomeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  StarIcon,
  BuildingOfficeIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

const PropertyCard = ({ property, onSelect, isSelected, onCompare }) => {
  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getInvestmentScoreColor = (score) => {
    if (!score) return 'text-gray-500';
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getDaysUntilSale = (saleDate) => {
    if (!saleDate) return null;
    const today = new Date();
    const sale = new Date(saleDate);
    const diffTime = sale - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysUntilSale = getDaysUntilSale(property.next_sale_date);
  const hasUpcomingSale = property.next_sale_date && daysUntilSale > 0;

  return (
    <div className={`property-card card hover:shadow-lg transition-all duration-200 cursor-pointer ${isSelected ? 'ring-2 ring-tax-primary' : ''}`}>
      <div className="card-body p-4">
        {/* Header with Selection and Investment Score */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-start space-x-3">
            {onCompare && (
              <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                  e.stopPropagation();
                  onCompare(property, e.target.checked);
                }}
                className="mt-1 h-4 w-4 text-tax-primary focus:ring-tax-primary border-gray-300 rounded"
              />
            )}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                {property.property_address || 'Address Not Available'}
              </h3>
              <div className="flex items-center mt-1 text-sm text-gray-600">
                <MapPinIcon className="h-4 w-4 mr-1" />
                <span>
                  {property.city ? `${property.city}, ` : ''}
                  {property.state || 'TX'}
                  {property.zip_code ? ` ${property.zip_code}` : ''}
                </span>
              </div>
            </div>
          </div>
          
          {/* Investment Score Badge */}
          {property.investment_score && (
            <div className={`px-3 py-1 rounded-full text-sm font-bold ${getInvestmentScoreColor(property.investment_score)}`}>
              {Math.round(property.investment_score)}
            </div>
          )}
        </div>

        {/* Property Image Placeholder */}
        {property.property_images && property.property_images.length > 0 ? (
          <div className="relative mb-4 h-48 bg-gray-200 rounded-lg overflow-hidden">
            <img
              src={property.property_images[0]}
              alt={property.property_address}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="relative mb-4 h-48 bg-gray-100 rounded-lg flex items-center justify-center">
            <HomeIcon className="h-12 w-12 text-gray-400" />
          </div>
        )}

        {/* Key Property Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Property Type</p>
            <p className="font-medium text-sm">{property.property_type || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Owner</p>
            <p className="font-medium text-sm truncate" title={property.owner_name}>
              {property.owner_name || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">County</p>
            <p className="font-medium text-sm">{property.county_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Parcel #</p>
            <p className="font-medium text-sm truncate" title={property.parcel_number}>
              {property.parcel_number || 'N/A'}
            </p>
          </div>
        </div>

        {/* Financial Information */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="flex items-center mb-1">
              <CurrencyDollarIcon className="h-4 w-4 text-blue-600 mr-1" />
              <span className="text-xs text-blue-700 font-medium">Assessed Value</span>
            </div>
            <p className="text-lg font-bold text-blue-800">
              {formatCurrency(property.assessed_value)}
            </p>
          </div>
          
          {property.zestimate && (
            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="flex items-center mb-1">
                <HomeIcon className="h-4 w-4 text-purple-600 mr-1" />
                <span className="text-xs text-purple-700 font-medium">Zestimate®</span>
              </div>
              <p className="text-lg font-bold text-purple-800">
                {formatCurrency(property.zestimate)}
              </p>
            </div>
          )}
        </div>

        {/* Investment Metrics */}
        {(property.roi_percentage || property.monthly_rent_estimate) && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            {property.roi_percentage && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Est. ROI</p>
                <p className="text-lg font-bold text-green-600">
                  {property.roi_percentage.toFixed(1)}%
                </p>
              </div>
            )}
            {property.monthly_rent_estimate && (
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Est. Rent</p>
                <p className="text-lg font-bold text-green-600">
                  {formatCurrency(property.monthly_rent_estimate)}/mo
                </p>
              </div>
            )}
          </div>
        )}

        {/* Tax Sale Information */}
        {hasUpcomingSale && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CalendarIcon className="h-5 w-5 text-yellow-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    Tax Sale: {new Date(property.next_sale_date).toLocaleDateString()}
                  </p>
                  <div className="flex items-center mt-1 text-xs text-yellow-700">
                    <ClockIcon className="h-3 w-3 mr-1" />
                    <span className="font-medium">
                      {daysUntilSale} days remaining
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-yellow-600">Min. Bid</p>
                <p className="font-bold text-yellow-800">
                  {formatCurrency(property.minimum_bid)}
                </p>
              </div>
            </div>
            {property.taxes_owed && (
              <div className="mt-2 pt-2 border-t border-yellow-300">
                <p className="text-xs text-yellow-700">
                  Taxes Owed: <span className="font-medium">{formatCurrency(property.taxes_owed)}</span>
                </p>
              </div>
            )}
          </div>
        )}

        {/* Property Features */}
        {(property.bedrooms || property.square_footage || property.year_built) && (
          <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
            {property.bedrooms && (
              <div className="text-center">
                <p className="font-medium">{property.bedrooms}</p>
                <p className="text-xs text-gray-500">Beds</p>
              </div>
            )}
            {property.square_footage && (
              <div className="text-center">
                <p className="font-medium">{property.square_footage.toLocaleString()}</p>
                <p className="text-xs text-gray-500">Sq Ft</p>
              </div>
            )}
            {property.year_built && (
              <div className="text-center">
                <p className="font-medium">{property.year_built}</p>
                <p className="text-xs text-gray-500">Built</p>
              </div>
            )}
          </div>
        )}

        {/* Neighborhood Info */}
        {(property.school_rating || property.walk_score) && (
          <div className="flex justify-between text-sm text-gray-600 pt-3 border-t border-gray-100">
            {property.school_rating && (
              <div className="flex items-center">
                <StarIcon className="h-4 w-4 mr-1" />
                <span>School: {property.school_rating.toFixed(1)}/10</span>
              </div>
            )}
            {property.walk_score && (
              <div className="flex items-center">
                <MapPinIcon className="h-4 w-4 mr-1" />
                <span>Walk Score: {property.walk_score}</span>
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={() => onSelect && onSelect(property)}
          className="w-full mt-4 bg-tax-primary text-white py-2 px-4 rounded-lg font-medium hover:bg-tax-primary/90 transition-colors"
        >
          View Details
        </button>
      </div>
    </div>
  );
};

export default PropertyCard;