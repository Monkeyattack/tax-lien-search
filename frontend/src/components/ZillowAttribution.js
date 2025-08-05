import React from 'react';

const ZillowAttribution = () => {
  return (
    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
      <div className="flex items-center">
        <svg className="h-5 w-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
        <p className="text-sm text-blue-800">
          <strong>Data by Zillow®</strong> - Property details, Zestimate®, and neighborhood information provided by Zillow Group.
        </p>
      </div>
      <p className="text-xs text-blue-600 mt-1">
        © Zillow, Inc., 2006-2024. Use is subject to Terms of Use. Zestimate® is a registered trademark of Zillow, Inc.
      </p>
    </div>
  );
};

export default ZillowAttribution;