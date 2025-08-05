import React, { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import api from '../services/authService';
import { toast } from 'react-toastify';
import { XMarkIcon } from '@heroicons/react/24/outline';

const SaveSearchModal = ({ isOpen, onClose, filters }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [alertFrequency, setAlertFrequency] = useState('daily');
  
  const queryClient = useQueryClient();
  
  const { mutate: saveSearch, isLoading } = useMutation(
    (data) => api.post('/saved-searches', data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['saved-searches']);
        toast.success('Search saved successfully!');
        onClose();
        resetForm();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to save search');
      }
    }
  );
  
  const resetForm = () => {
    setName('');
    setDescription('');
    setEmailAlerts(true);
    setAlertFrequency('daily');
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast.error('Please enter a name for your saved search');
      return;
    }
    
    saveSearch({
      name: name.trim(),
      description: description.trim(),
      filters,
      email_alerts: emailAlerts,
      alert_frequency: alertFrequency
    });
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Save Search</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tax-primary"
              placeholder="e.g., Dallas High ROI Properties"
              maxLength={255}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tax-primary"
              placeholder="Add notes about this search..."
              rows={3}
            />
          </div>
          
          <div className="border-t pt-4">
            <h3 className="font-medium mb-3">Alert Preferences</h3>
            
            <div className="flex items-center mb-3">
              <input
                type="checkbox"
                id="emailAlerts"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="h-4 w-4 text-tax-primary focus:ring-tax-primary border-gray-300 rounded"
              />
              <label htmlFor="emailAlerts" className="ml-2 text-sm text-gray-700">
                Email me when new properties match this search
              </label>
            </div>
            
            {emailAlerts && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alert Frequency
                </label>
                <select
                  value={alertFrequency}
                  onChange={(e) => setAlertFrequency(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-tax-primary"
                >
                  <option value="instant">Instant</option>
                  <option value="daily">Daily Summary</option>
                  <option value="weekly">Weekly Summary</option>
                </select>
              </div>
            )}
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-tax-primary text-white rounded-md hover:bg-tax-secondary disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Search'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SaveSearchModal;