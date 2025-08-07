import React, { useState } from 'react';
import {
  MapPinIcon,
  GlobeAltIcon,
  PhotoIcon,
  ArrowTopRightOnSquareIcon,
  EyeIcon,
  MapIcon,
} from '@heroicons/react/24/outline';

const PropertyDetailMap = ({ property }) => {
  const [activeTab, setActiveTab] = useState('map');

  const formatAddress = (property) => {
    const parts = [
      property.property_address,
      property.city,
      property.state || 'TX',
      property.zip_code
    ].filter(Boolean);
    return parts.join(', ');
  };

  const address = formatAddress(property);
  const encodedAddress = encodeURIComponent(address);

  // Google Maps URLs
  const googleMapsUrl = `https://www.google.com/maps/search/${encodedAddress}`;
  const streetViewUrl = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${property.latitude || ''},${property.longitude || ''}&heading=0&pitch=0`;
  const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`;

  // Embedded Google Maps iframe URL
  const embedMapUrl = `https://www.google.com/maps/embed/v1/place?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&q=${encodedAddress}&zoom=16`;
  const embedStreetViewUrl = `https://www.google.com/maps/embed/v1/streetview?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&location=${encodedAddress}&heading=0&pitch=0&fov=80`;

  const hasGoogleMapsKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

  const ExternalLinkButton = ({ href, icon: Icon, text, className }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-tax-primary ${className}`}
    >
      <Icon className="h-4 w-4 mr-2" />
      {text}
      <ArrowTopRightOnSquareIcon className="h-3 w-3 ml-1" />
    </a>
  );

  return (
    <div className="space-y-4">
      {/* Property Location Header */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <MapPinIcon className="h-6 w-6 text-tax-primary flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900">Property Location</h3>
            <p className="text-gray-600 mt-1">{address}</p>
            {property.latitude && property.longitude && (
              <p className="text-sm text-gray-500 mt-1">
                Coordinates: {property.latitude}, {property.longitude}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* External Links */}
      <div className="flex flex-wrap gap-2">
        <ExternalLinkButton
          href={googleMapsUrl}
          icon={MapIcon}
          text="Google Maps"
        />
        <ExternalLinkButton
          href={streetViewUrl}
          icon={EyeIcon}
          text="Street View"
        />
        <ExternalLinkButton
          href={directionsUrl}
          icon={MapPinIcon}
          text="Get Directions"
        />
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {[
            { id: 'map', label: 'Map View', icon: MapIcon },
            { id: 'streetview', label: 'Street View', icon: EyeIcon },
            { id: 'photos', label: 'Photos', icon: PhotoIcon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-tax-primary text-tax-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'map' && (
          <div className="space-y-4">
            {hasGoogleMapsKey ? (
              <div className="relative h-96 bg-gray-200 rounded-lg overflow-hidden">
                <iframe
                  src={embedMapUrl}
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  allowFullScreen=""
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Property Map"
                  className="rounded-lg"
                />
              </div>
            ) : (
              <div className="h-96 bg-gray-100 rounded-lg flex flex-col items-center justify-center text-center p-8">
                <MapIcon className="h-16 w-16 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Interactive Map Not Available</h3>
                <p className="text-gray-600 mb-4">
                  Google Maps API key is not configured. You can still view the property location using the external links above.
                </p>
                <ExternalLinkButton
                  href={googleMapsUrl}
                  icon={MapIcon}
                  text="Open in Google Maps"
                  className="bg-tax-primary text-white border-tax-primary hover:bg-tax-primary/90"
                />
              </div>
            )}
          </div>
        )}

        {activeTab === 'streetview' && (
          <div className="space-y-4">
            {hasGoogleMapsKey ? (
              <div className="relative h-96 bg-gray-200 rounded-lg overflow-hidden">
                <iframe
                  src={embedStreetViewUrl}
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  allowFullScreen=""
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Property Street View"
                  className="rounded-lg"
                />
              </div>
            ) : (
              <div className="h-96 bg-gray-100 rounded-lg flex flex-col items-center justify-center text-center p-8">
                <EyeIcon className="h-16 w-16 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Street View Not Available</h3>
                <p className="text-gray-600 mb-4">
                  Google Maps API key is not configured. You can still access Street View using the external link.
                </p>
                <ExternalLinkButton
                  href={streetViewUrl}
                  icon={EyeIcon}
                  text="Open Street View"
                  className="bg-tax-primary text-white border-tax-primary hover:bg-tax-primary/90"
                />
              </div>
            )}
          </div>
        )}

        {activeTab === 'photos' && (
          <div className="space-y-4">
            {property.property_images && property.property_images.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {property.property_images.map((image, index) => (
                  <div key={index} className="relative aspect-video bg-gray-200 rounded-lg overflow-hidden">
                    <img
                      src={image}
                      alt={`Property view ${index + 1}`}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-96 bg-gray-100 rounded-lg flex flex-col items-center justify-center text-center p-8">
                <PhotoIcon className="h-16 w-16 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Photos Available</h3>
                <p className="text-gray-600 mb-4">
                  Property photos haven't been uploaded yet. You can view the property using Street View or satellite imagery.
                </p>
                <div className="flex space-x-3">
                  <ExternalLinkButton
                    href={streetViewUrl}
                    icon={EyeIcon}
                    text="Street View"
                  />
                  <ExternalLinkButton
                    href={googleMapsUrl}
                    icon={GlobeAltIcon}
                    text="Satellite View"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Property Coordinates */}
      {property.latitude && property.longitude && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">GPS Coordinates</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-blue-700">Latitude:</span>
              <span className="font-mono ml-2">{property.latitude}</span>
            </div>
            <div>
              <span className="text-blue-700">Longitude:</span>
              <span className="font-mono ml-2">{property.longitude}</span>
            </div>
          </div>
        </div>
      )}

      {/* Neighborhood Information */}
      {(property.school_rating || property.walk_score) && (
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-medium text-green-900 mb-3">Neighborhood Insights</h4>
          <div className="grid grid-cols-2 gap-4">
            {property.school_rating && (
              <div className="text-center">
                <div className="text-2xl font-bold text-green-800">
                  {property.school_rating.toFixed(1)}/10
                </div>
                <div className="text-sm text-green-700">School Rating</div>
              </div>
            )}
            {property.walk_score && (
              <div className="text-center">
                <div className="text-2xl font-bold text-green-800">
                  {property.walk_score}
                </div>
                <div className="text-sm text-green-700">Walk Score</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyDetailMap;