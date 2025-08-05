import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import api from '../services/authService';
import { toast } from 'react-toastify';
import {
  BellIcon,
  MagnifyingGlassIcon,
  TrashIcon,
  PencilIcon,
  PlayIcon,
  PauseIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import GoogleAd from '../components/GoogleAd';

const SavedSearches = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [editingSearch, setEditingSearch] = useState(null);
  
  // Fetch saved searches
  const { data: searches, isLoading } = useQuery(
    'saved-searches',
    () => api.get('/saved-searches').then(res => res.data)
  );
  
  // Delete mutation
  const { mutate: deleteSearch } = useMutation(
    (searchId) => api.delete(`/saved-searches/${searchId}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['saved-searches']);
        toast.success('Search deleted successfully');
      },
      onError: () => {
        toast.error('Failed to delete search');
      }
    }
  );
  
  // Toggle active mutation
  const { mutate: updateSearch } = useMutation(
    ({ searchId, data }) => api.put(`/saved-searches/${searchId}`, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['saved-searches']);
        toast.success('Search updated successfully');
      },
      onError: () => {
        toast.error('Failed to update search');
      }
    }
  );
  
  // Run search mutation
  const { mutate: runSearch } = useMutation(
    (searchId) => api.post(`/saved-searches/${searchId}/run`),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['saved-searches']);
        toast.success(data.data.message);
      },
      onError: () => {
        toast.error('Failed to run search');
      }
    }
  );
  
  const handleDelete = (searchId) => {
    if (window.confirm('Are you sure you want to delete this saved search?')) {
      deleteSearch(searchId);
    }
  };
  
  const toggleActive = (search) => {
    updateSearch({
      searchId: search.id,
      data: { is_active: !search.is_active }
    });
  };
  
  const getFrequencyIcon = (frequency) => {
    switch (frequency) {
      case 'instant':
        return <ExclamationCircleIcon className="h-4 w-4" />;
      case 'daily':
        return <ClockIcon className="h-4 w-4" />;
      case 'weekly':
        return <CheckCircleIcon className="h-4 w-4" />;
      default:
        return null;
    }
  };
  
  const formatFilters = (filters) => {
    const parts = [];
    
    if (filters.counties?.length) {
      parts.push(`Counties: ${filters.counties.length}`);
    }
    if (filters.property_types?.length) {
      parts.push(`Types: ${filters.property_types.join(', ')}`);
    }
    if (filters.min_value || filters.max_value) {
      const range = [];
      if (filters.min_value) range.push(`$${filters.min_value.toLocaleString()}`);
      if (filters.max_value) range.push(`$${filters.max_value.toLocaleString()}`);
      parts.push(`Value: ${range.join(' - ')}`);
    }
    if (filters.min_investment_score) {
      parts.push(`Min Score: ${filters.min_investment_score}`);
    }
    
    return parts.join(' • ') || 'No filters';
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tax-primary"></div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Saved Searches</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your saved property searches and alerts
          </p>
        </div>
        <button
          onClick={() => navigate('/properties')}
          className="btn-primary flex items-center"
        >
          <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
          New Search
        </button>
      </div>
      
      {/* Top Ad */}
      <GoogleAd adSlot="top-banner" />
      
      {/* Saved Searches List */}
      {searches && searches.length > 0 ? (
        <div className="grid gap-4">
          {searches.map((search) => (
            <div key={search.id} className="card hover:shadow-lg transition-shadow">
              <div className="card-body">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{search.name}</h3>
                      {search.is_active ? (
                        <span className="px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
                          Inactive
                        </span>
                      )}
                      {search.email_alerts && (
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <BellIcon className="h-4 w-4" />
                          <span className="flex items-center gap-1">
                            {getFrequencyIcon(search.alert_frequency)}
                            {search.alert_frequency}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {search.description && (
                      <p className="text-sm text-gray-600 mb-2">{search.description}</p>
                    )}
                    
                    <div className="text-sm text-gray-500 mb-3">
                      {formatFilters(search.filters)}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-600">
                        {search.match_count} properties
                      </span>
                      {search.new_matches_count > 0 && (
                        <span className="text-tax-primary font-medium">
                          {search.new_matches_count} new
                        </span>
                      )}
                      {search.last_alert_sent && (
                        <span className="text-gray-500">
                          Last alert: {new Date(search.last_alert_sent).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => navigate(`/properties?search=${search.id}`)}
                      className="p-2 text-gray-600 hover:text-tax-primary hover:bg-gray-100 rounded"
                      title="View Results"
                    >
                      <MagnifyingGlassIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => runSearch(search.id)}
                      className="p-2 text-gray-600 hover:text-tax-primary hover:bg-gray-100 rounded"
                      title="Run Search Now"
                    >
                      <PlayIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => toggleActive(search)}
                      className="p-2 text-gray-600 hover:text-tax-primary hover:bg-gray-100 rounded"
                      title={search.is_active ? 'Pause' : 'Activate'}
                    >
                      {search.is_active ? (
                        <PauseIcon className="h-5 w-5" />
                      ) : (
                        <PlayIcon className="h-5 w-5" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDelete(search.id)}
                      className="p-2 text-gray-600 hover:text-red-600 hover:bg-gray-100 rounded"
                      title="Delete"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="card-body text-center py-12">
            <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No saved searches</h3>
            <p className="text-gray-500 mb-6">
              Save your property searches to get alerts when new matches are found
            </p>
            <button
              onClick={() => navigate('/properties')}
              className="btn-primary mx-auto"
            >
              Create Your First Search
            </button>
          </div>
        </div>
      )}
      
      {/* Bottom Ad */}
      <GoogleAd adSlot="bottom-banner" />
    </div>
  );
};

export default SavedSearches;