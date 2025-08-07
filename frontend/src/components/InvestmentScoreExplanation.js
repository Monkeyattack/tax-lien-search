import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ChartBarIcon,
  HomeIcon,
  CurrencyDollarIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  AcademicCapIcon,
  ShieldCheckIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  CalculatorIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';

const InvestmentScoreExplanation = () => {
  const navigate = useNavigate();

  const scoreFactors = [
    {
      icon: <CurrencyDollarIcon className="h-6 w-6" />,
      title: "ROI Potential",
      weight: "30%",
      description: "Return on Investment based on estimated value vs. minimum bid",
      breakdown: [
        { range: ">100% ROI", points: 30, label: "Exceptional" },
        { range: "50-100% ROI", points: 20, label: "Very Good" },
        { range: "25-50% ROI", points: 10, label: "Good" },
        { range: "<25% ROI", points: 0, label: "Low" },
      ]
    },
    {
      icon: <MapPinIcon className="h-6 w-6" />,
      title: "Location Quality",
      weight: "20%",
      description: "Neighborhood crime rates, walkability, and amenities",
      breakdown: [
        { range: "Low crime + High walkability", points: 20, label: "Premium" },
        { range: "Low crime OR High walkability", points: 10, label: "Good" },
        { range: "Average area", points: 5, label: "Standard" },
        { range: "High crime area", points: 0, label: "Challenging" },
      ]
    },
    {
      icon: <AcademicCapIcon className="h-6 w-6" />,
      title: "School District",
      weight: "20%",
      description: "Quality of nearby schools affects property values",
      breakdown: [
        { range: "School rating >8/10", points: 20, label: "Excellent" },
        { range: "School rating 6-8/10", points: 10, label: "Good" },
        { range: "School rating 4-6/10", points: 5, label: "Average" },
        { range: "School rating <4/10", points: 0, label: "Below Average" },
      ]
    },
    {
      icon: <BuildingOfficeIcon className="h-6 w-6" />,
      title: "Property Condition",
      weight: "20%",
      description: "Based on year built and estimated renovation needs",
      breakdown: [
        { range: "Built after 2000", points: 20, label: "Modern" },
        { range: "Built 1980-2000", points: 10, label: "Updated" },
        { range: "Built 1960-1980", points: 5, label: "Older" },
        { range: "Built before 1960", points: 0, label: "Vintage" },
      ]
    },
    {
      icon: <ArrowTrendingUpIcon className="h-6 w-6" />,
      title: "Market Trends",
      weight: "10%",
      description: "Area appreciation rates and market demand",
      breakdown: [
        { range: "High growth area", points: 10, label: "Hot Market" },
        { range: "Stable growth", points: 5, label: "Steady" },
        { range: "Flat market", points: 2, label: "Stable" },
        { range: "Declining area", points: 0, label: "Challenging" },
      ]
    },
  ];

  const getScoreColor = (score) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Investment';
    if (score >= 60) return 'Good Investment';
    if (score >= 40) return 'Fair Investment';
    return 'High Risk Investment';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-tax-primary hover:text-tax-primary/80 mb-4"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Properties
          </button>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center mb-4">
              <ChartBarIcon className="h-8 w-8 text-tax-primary mr-3" />
              <h1 className="text-3xl font-bold text-gray-900">
                Investment Score Explained
              </h1>
            </div>
            <p className="text-gray-600">
              Our proprietary Investment Score helps you quickly identify the most promising 
              tax lien investment opportunities. The score ranges from 0-100 and considers 
              multiple factors that affect investment potential and risk.
            </p>
          </div>
        </div>

        {/* Score Ranges */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Score Ranges</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 rounded-lg bg-green-50 border border-green-200">
              <div className="text-3xl font-bold text-green-600">80-100</div>
              <div className="text-sm font-medium text-green-700 mt-1">Excellent</div>
              <div className="text-xs text-gray-600 mt-2">Prime investment opportunity</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-yellow-50 border border-yellow-200">
              <div className="text-3xl font-bold text-yellow-600">60-79</div>
              <div className="text-sm font-medium text-yellow-700 mt-1">Good</div>
              <div className="text-xs text-gray-600 mt-2">Solid potential with moderate risk</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-orange-50 border border-orange-200">
              <div className="text-3xl font-bold text-orange-600">40-59</div>
              <div className="text-sm font-medium text-orange-700 mt-1">Fair</div>
              <div className="text-xs text-gray-600 mt-2">Higher risk, needs careful analysis</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-red-50 border border-red-200">
              <div className="text-3xl font-bold text-red-600">0-39</div>
              <div className="text-sm font-medium text-red-700 mt-1">High Risk</div>
              <div className="text-xs text-gray-600 mt-2">Significant challenges expected</div>
            </div>
          </div>
        </div>

        {/* Scoring Factors */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Scoring Factors</h2>
          
          {scoreFactors.map((factor, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-start mb-4">
                <div className="flex-shrink-0 p-2 bg-tax-primary/10 rounded-lg text-tax-primary mr-4">
                  {factor.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold">{factor.title}</h3>
                    <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium">
                      Weight: {factor.weight}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{factor.description}</p>
                  
                  <div className="space-y-2">
                    {factor.breakdown.map((level, levelIndex) => (
                      <div key={levelIndex} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                        <div className="flex items-center">
                          <span className="text-sm text-gray-700">{level.range}</span>
                          <span className="ml-3 px-2 py-0.5 bg-gray-100 rounded text-xs font-medium text-gray-600">
                            {level.label}
                          </span>
                        </div>
                        <span className="text-sm font-semibold text-tax-primary">
                          +{level.points} points
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Information */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start">
            <ShieldCheckIcon className="h-6 w-6 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Important Note</h3>
              <p className="text-sm text-blue-800">
                The Investment Score is a guideline based on available data and should not be 
                the sole factor in your investment decision. Always conduct thorough due diligence, 
                including property inspection, title research, and consultation with legal and 
                financial advisors before bidding on tax lien properties.
              </p>
            </div>
          </div>
        </div>

        {/* Data Sources */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold mb-4">Data Sources</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span>County Tax Records</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span>Zillow Public Data</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span>Google Maps & Places</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span>Public School Ratings</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestmentScoreExplanation;