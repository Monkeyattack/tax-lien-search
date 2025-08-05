import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PropertySearch from '../components/PropertySearch';
import GoogleAd from '../components/GoogleAd';

const Properties = () => {
  const navigate = useNavigate();
  const [selectedProperty, setSelectedProperty] = useState(null);

  const handlePropertySelect = (property) => {
    navigate(`/properties/${property.id}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Property Search</h1>
        <p className="mt-1 text-sm text-gray-500">
          Search tax sale properties with advanced filters and investment analysis
        </p>
      </div>
      
      {/* Top Banner Ad */}
      <GoogleAd adSlot="top-banner" />
      
      {/* Property Search Component */}
      <PropertySearch onPropertySelect={handlePropertySelect} />
      
      {/* Bottom Banner Ad */}
      <GoogleAd adSlot="bottom-banner" />
    </div>
  );
};

export default Properties;