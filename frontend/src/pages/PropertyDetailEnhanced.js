import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import api from '../services/authService';
import GoogleAd from '../components/GoogleAd';
import ZillowAttribution from '../components/ZillowAttribution';
import {
  HomeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  DocumentTextIcon,
  ChartBarIcon,
  AcademicCapIcon,
  BuildingOfficeIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import { StarIcon } from '@heroicons/react/24/solid';

const PropertyDetailEnhanced = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch property details with enrichment
  const { data: property, isLoading } = useQuery(
    ['property', id],
    () => api.get(`/properties/${id}/enriched`).then(res => res.data)
  );

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tax-primary"></div>
      </div>
    );
  }

  if (!property) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">Property not found</p>
      </div>
    );
  }

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
    if (!score) return 'bg-gray-200 text-gray-600';
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="px-4 py-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {property.property_address}
              </h1>
              <p className="text-gray-600 mt-1">
                {property.city}, {property.state} {property.zip_code}
              </p>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                <span>Parcel: {property.parcel_number}</span>
                <span>•</span>
                <span>Owner: {property.owner_name}</span>
              </div>
            </div>
            {property.enrichment?.investment_score && (
              <div className={`px-6 py-3 rounded-lg text-center ${getInvestmentScoreColor(property.enrichment.investment_score)}`}>
                <div className="text-3xl font-bold">{Math.round(property.enrichment.investment_score)}</div>
                <div className="text-sm">Investment Score</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top Ad */}
      <GoogleAd adSlot="in-content" />

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'valuation', 'neighborhood', 'tax-history', 'investment'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-tax-primary text-tax-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <>
              <div className="card">
                <div className="card-header">
                  <h2 className="text-lg font-semibold">Property Details</h2>
                </div>
                <div className="card-body">
                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Property Type</dt>
                      <dd className="text-sm text-gray-900">{property.property_type || 'N/A'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Year Built</dt>
                      <dd className="text-sm text-gray-900">{property.year_built || 'N/A'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Square Footage</dt>
                      <dd className="text-sm text-gray-900">
                        {property.square_footage ? property.square_footage.toLocaleString() : 'N/A'} sq ft
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Lot Size</dt>
                      <dd className="text-sm text-gray-900">
                        {property.lot_size ? `${property.lot_size.toLocaleString()} sq ft` : 'N/A'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Bedrooms</dt>
                      <dd className="text-sm text-gray-900">{property.bedrooms || 'N/A'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Bathrooms</dt>
                      <dd className="text-sm text-gray-900">{property.bathrooms || 'N/A'}</dd>
                    </div>
                  </dl>
                </div>
              </div>

              {/* Tax Sale Info */}
              {property.next_tax_sale && (
                <div className="card border-yellow-200 bg-yellow-50">
                  <div className="card-body">
                    <div className="flex items-center mb-4">
                      <CalendarIcon className="h-6 w-6 text-yellow-600 mr-2" />
                      <h3 className="text-lg font-semibold text-yellow-800">Upcoming Tax Sale</h3>
                    </div>
                    <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-yellow-700">Sale Date</dt>
                        <dd className="text-sm text-yellow-900 font-semibold">
                          {new Date(property.next_tax_sale.sale_date).toLocaleDateString()}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-yellow-700">Minimum Bid</dt>
                        <dd className="text-sm text-yellow-900 font-semibold">
                          {formatCurrency(property.next_tax_sale.minimum_bid)}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-yellow-700">Taxes Owed</dt>
                        <dd className="text-sm text-yellow-900">
                          {formatCurrency(property.next_tax_sale.taxes_owed)}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-yellow-700">Total Judgment</dt>
                        <dd className="text-sm text-yellow-900">
                          {formatCurrency(property.next_tax_sale.total_judgment)}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
              )}
            </>
          )}

          {/* Valuation Tab */}
          {activeTab === 'valuation' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h2 className="text-lg font-semibold">Property Valuation</h2>
                </div>
                <div className="card-body">
                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Assessed Value</dt>
                      <dd className="text-2xl font-semibold text-gray-900">
                        {formatCurrency(property.assessed_value)}
                      </dd>
                    </div>
                    {property.enrichment?.zestimate && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Zestimate®</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {formatCurrency(property.enrichment.zestimate)}
                        </dd>
                      </div>
                    )}
                    {property.enrichment?.monthly_rent_estimate && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Estimated Monthly Rent</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {formatCurrency(property.enrichment.monthly_rent_estimate)}
                        </dd>
                      </div>
                    )}
                    {property.enrichment?.gross_rent_multiplier && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Gross Rent Multiplier</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {property.enrichment.gross_rent_multiplier.toFixed(1)}
                        </dd>
                      </div>
                    )}
                  </dl>
                </div>
              </div>

              {/* Price History from Zillow */}
              {property.enrichment?.zillow_price_history && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="text-lg font-semibold">Price History</h3>
                  </div>
                  <div className="card-body">
                    <div className="space-y-3">
                      {property.enrichment.zillow_price_history.map((entry, index) => (
                        <div key={index} className="flex justify-between items-center py-2 border-b last:border-0">
                          <div>
                            <p className="font-medium">{entry.date}</p>
                            <p className="text-sm text-gray-500">{entry.event}</p>
                          </div>
                          <p className="font-semibold">{formatCurrency(entry.price)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <ZillowAttribution />
            </div>
          )}

          {/* Neighborhood Tab */}
          {activeTab === 'neighborhood' && (
            <div className="space-y-6">
              {/* Nearby Schools */}
              {property.enrichment?.nearby_schools && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="text-lg font-semibold flex items-center">
                      <AcademicCapIcon className="h-5 w-5 mr-2" />
                      Nearby Schools
                    </h3>
                  </div>
                  <div className="card-body">
                    <div className="space-y-3">
                      {property.enrichment.nearby_schools.map((school, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <div>
                            <p className="font-medium">{school.name}</p>
                            <p className="text-sm text-gray-500">{school.distance_miles} miles</p>
                          </div>
                          {school.rating && (
                            <div className="flex items-center">
                              <StarIcon className="h-5 w-5 text-yellow-500 mr-1" />
                              <span className="font-semibold">{school.rating}/10</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Neighborhood Stats */}
              {property.enrichment?.neighborhood_data && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="text-lg font-semibold">Neighborhood Information</h3>
                  </div>
                  <div className="card-body">
                    <dl className="grid grid-cols-2 gap-4">
                      {property.enrichment.neighborhood_data.walk_score && (
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Walk Score</dt>
                          <dd className="text-2xl font-semibold">{property.enrichment.neighborhood_data.walk_score}</dd>
                        </div>
                      )}
                      {property.enrichment.neighborhood_data.transit_score && (
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Transit Score</dt>
                          <dd className="text-2xl font-semibold">{property.enrichment.neighborhood_data.transit_score}</dd>
                        </div>
                      )}
                      {property.enrichment.neighborhood_data.demographics?.crime_rate && (
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Crime Rate</dt>
                          <dd className="text-lg font-semibold">{property.enrichment.neighborhood_data.demographics.crime_rate}</dd>
                        </div>
                      )}
                      {property.enrichment.neighborhood_data.demographics?.median_income && (
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Median Income</dt>
                          <dd className="text-lg font-semibold">
                            {formatCurrency(property.enrichment.neighborhood_data.demographics.median_income)}
                          </dd>
                        </div>
                      )}
                    </dl>
                  </div>
                </div>
              )}

              <ZillowAttribution />
            </div>
          )}

          {/* Investment Analysis Tab */}
          {activeTab === 'investment' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold">Investment Analysis</h3>
                </div>
                <div className="card-body">
                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {property.enrichment?.roi_percentage && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Estimated ROI</dt>
                        <dd className="text-2xl font-semibold text-green-600">
                          {property.enrichment.roi_percentage.toFixed(1)}%
                        </dd>
                      </div>
                    )}
                    {property.enrichment?.cap_rate && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Cap Rate</dt>
                        <dd className="text-2xl font-semibold">
                          {property.enrichment.cap_rate.toFixed(2)}%
                        </dd>
                      </div>
                    )}
                    {property.enrichment?.cash_on_cash_return && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Cash on Cash Return</dt>
                        <dd className="text-2xl font-semibold">
                          {property.enrichment.cash_on_cash_return.toFixed(2)}%
                        </dd>
                      </div>
                    )}
                    {property.enrichment?.estimated_rehab_cost && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Est. Rehab Cost</dt>
                        <dd className="text-2xl font-semibold">
                          {formatCurrency(property.enrichment.estimated_rehab_cost)}
                        </dd>
                      </div>
                    )}
                  </dl>
                </div>
              </div>

              {/* Investment Breakdown */}
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold">Investment Breakdown</h3>
                </div>
                <div className="card-body">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Minimum Bid</span>
                      <span className="font-semibold">{formatCurrency(property.next_tax_sale?.minimum_bid || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Estimated Rehab</span>
                      <span className="font-semibold">{formatCurrency(property.enrichment?.estimated_rehab_cost || 20000)}</span>
                    </div>
                    <div className="flex justify-between pt-3 border-t">
                      <span className="font-medium">Total Investment</span>
                      <span className="font-bold text-lg">
                        {formatCurrency((property.next_tax_sale?.minimum_bid || 0) + (property.enrichment?.estimated_rehab_cost || 20000))}
                      </span>
                    </div>
                    <div className="flex justify-between pt-3">
                      <span className="text-gray-600">After Repair Value</span>
                      <span className="font-semibold text-green-600">
                        {formatCurrency(property.enrichment?.zestimate || property.assessed_value)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="card">
            <div className="card-body">
              <h3 className="font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button className="btn-primary w-full">
                  Track This Property
                </button>
                <button className="btn-secondary w-full">
                  Set Price Alert
                </button>
                <button className="btn-secondary w-full">
                  Download Report
                </button>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="card">
            <div className="card-body">
              <h3 className="font-semibold mb-4">Key Metrics</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Redemption Period</p>
                  <p className="font-semibold">{property.redemption_period_months} months</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Expected Penalty Rate</p>
                  <p className="font-semibold">{property.expected_penalty_rate}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">County</p>
                  <p className="font-semibold">{property.county?.name}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar Ad */}
          <GoogleAd adSlot="sidebar" />
        </div>
      </div>
    </div>
  );
};

export default PropertyDetailEnhanced;