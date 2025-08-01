import React from 'react';
import { useParams } from 'react-router-dom';

const PropertyDetail = () => {
  const { id } = useParams();
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Property Detail #{id}</h1>
      </div>
      
      <div className="card">
        <div className="card-body">
          <p className="text-gray-600">Property details coming soon...</p>
        </div>
      </div>
    </div>
  );
};

export default PropertyDetail;