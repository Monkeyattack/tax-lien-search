import React, { useEffect } from 'react';

const GoogleAd = ({ adSlot, adFormat = 'auto', fullWidthResponsive = true }) => {
  useEffect(() => {
    try {
      // Push the ad to the adsbygoogle array
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (err) {
      console.error('Google Ads error:', err);
    }
  }, []);

  // Different ad sizes based on slot
  const getAdStyle = () => {
    switch (adSlot) {
      case 'top-banner':
        return { display: 'block', minHeight: '90px' };
      case 'bottom-banner':
        return { display: 'block', minHeight: '90px' };
      case 'sidebar':
        return { display: 'block', minHeight: '250px' };
      case 'in-content':
        return { display: 'block', minHeight: '280px' };
      default:
        return { display: 'block' };
    }
  };

  // In development, show placeholder
  if (process.env.NODE_ENV === 'development') {
    return (
      <div 
        className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-500"
        style={getAdStyle()}
      >
        <div className="text-center">
          <p className="font-semibold">Google Ad Space</p>
          <p className="text-sm">{adSlot}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="google-ad-container">
      <ins
        className="adsbygoogle"
        style={getAdStyle()}
        data-ad-client={process.env.REACT_APP_GOOGLE_ADS_CLIENT}
        data-ad-slot={process.env[`REACT_APP_GOOGLE_ADS_SLOT_${adSlot.toUpperCase().replace('-', '_')}`]}
        data-ad-format={adFormat}
        data-full-width-responsive={fullWidthResponsive}
      />
    </div>
  );
};

export default GoogleAd;