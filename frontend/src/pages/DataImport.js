import React, { useState } from 'react';
import { useMutation, useQuery } from 'react-query';
import api from '../services/authService';
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  TableCellsIcon,
  ArrowDownTrayIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const DataImport = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [importType, setImportType] = useState('properties');
  const [validationResult, setValidationResult] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [scrapingStatus, setScrapingStatus] = useState({});

  // Validate file mutation
  const validateMutation = useMutation(
    async (formData) => {
      const response = await api.post(`/data-import/validate?import_type=${importType}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setValidationResult(data);
      },
    }
  );

  // Import file mutation
  const importMutation = useMutation(
    async (formData) => {
      const endpoint = importType === 'properties' 
        ? '/data-import/csv/properties' 
        : '/data-import/csv/tax-sales';
      const response = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setImportResult(data);
        setSelectedFile(null);
        setValidationResult(null);
      },
    }
  );

  // Scrape data mutation
  const scrapeMutation = useMutation(
    async (countyCode) => {
      const response = await api.post(`/data-import/scrape/${countyCode}`);
      return response.data;
    },
    {
      onMutate: (countyCode) => {
        setScrapingStatus(prev => ({
          ...prev,
          [countyCode]: { status: 'starting', message: 'Initializing scraper...' }
        }));
      },
      onSuccess: (data, countyCode) => {
        setScrapingStatus(prev => ({
          ...prev,
          [countyCode]: { 
            status: 'running', 
            message: 'Scraping in progress. This may take several minutes...', 
            jobId: data.jobId 
          }
        }));
        // Start polling for status
        if (data.jobId) {
          pollScrapingStatus(data.jobId, countyCode);
        }
      },
      onError: (error, countyCode) => {
        setScrapingStatus(prev => ({
          ...prev,
          [countyCode]: { 
            status: 'error', 
            message: error.response?.data?.detail || 'Scraping failed' 
          }
        }));
      }
    }
  );

  // Poll for scraping status
  const pollScrapingStatus = async (jobId, countyCode) => {
    const checkStatus = async () => {
      try {
        const response = await api.get(`/data-import/scrape/status/${jobId}`);
        const data = response.data;
        
        setScrapingStatus(prev => ({
          ...prev,
          [countyCode]: {
            status: data.status,
            message: data.message,
            progress: data.progress,
            propertiesFound: data.properties_found,
            salesFound: data.sales_found
          }
        }));
        
        // Continue polling if still running
        if (data.status === 'running' || data.status === 'pending') {
          setTimeout(checkStatus, 3000); // Poll every 3 seconds
        }
      } catch (error) {
        console.error('Error checking scraping status:', error);
      }
    };
    
    checkStatus();
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setValidationResult(null);
    setImportResult(null);
  };

  const handleValidate = () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    validateMutation.mutate(formData);
  };

  const handleImport = () => {
    if (!selectedFile || !validationResult?.valid) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    importMutation.mutate(formData);
  };

  const downloadTemplate = async (templateType) => {
    try {
      const response = await api.get(`/data-import/templates/${templateType}`);
      const data = response.data;
      
      // Convert to CSV
      const headers = data.columns.join(',');
      const sample = data.sample_data[0];
      const values = data.columns.map(col => sample[col] || '').join(',');
      const csv = `${headers}\n${values}`;
      
      // Download
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${templateType}_template.csv`;
      a.click();
    } catch (error) {
      console.error('Error downloading template:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Data Import</h1>
        <p className="mt-1 text-sm text-gray-500">
          Import property and tax sale data from CSV files or scrape from county websites
        </p>
      </div>

      {/* Import Type Selection */}
      <div className="card">
        <div className="card-body">
          <h3 className="text-lg font-medium mb-4">Import Type</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setImportType('properties')}
              className={`p-4 border rounded-lg ${
                importType === 'properties' 
                  ? 'border-tax-primary bg-tax-primary/10' 
                  : 'border-gray-300'
              }`}
            >
              <DocumentTextIcon className="h-8 w-8 mx-auto mb-2" />
              <p className="font-medium">Properties</p>
              <p className="text-sm text-gray-500">Import property records</p>
            </button>
            
            <button
              onClick={() => setImportType('tax_sales')}
              className={`p-4 border rounded-lg ${
                importType === 'tax_sales' 
                  ? 'border-tax-primary bg-tax-primary/10' 
                  : 'border-gray-300'
              }`}
            >
              <TableCellsIcon className="h-8 w-8 mx-auto mb-2" />
              <p className="font-medium">Tax Sales</p>
              <p className="text-sm text-gray-500">Import tax sale listings</p>
            </button>
          </div>
        </div>
      </div>

      {/* File Upload */}
      <div className="card">
        <div className="card-body">
          <h3 className="text-lg font-medium mb-4">Upload CSV File</h3>
          
          <div className="mb-4">
            <button
              onClick={() => downloadTemplate(importType)}
              className="btn-secondary inline-flex items-center"
            >
              <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
              Download Template
            </button>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">
                {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
              </p>
              <p className="text-xs text-gray-500">CSV files only</p>
            </label>
          </div>

          {selectedFile && (
            <div className="mt-4 flex gap-2">
              <button
                onClick={handleValidate}
                disabled={validateMutation.isLoading}
                className="btn-secondary"
              >
                {validateMutation.isLoading ? 'Validating...' : 'Validate File'}
              </button>
              
              {validationResult?.valid && (
                <button
                  onClick={handleImport}
                  disabled={importMutation.isLoading}
                  className="btn-primary"
                >
                  {importMutation.isLoading ? 'Importing...' : 'Import Data'}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Validation Results */}
      {validationResult && (
        <div className={`card ${validationResult.valid ? 'border-green-200' : 'border-red-200'}`}>
          <div className="card-body">
            <div className="flex items-center mb-4">
              {validationResult.valid ? (
                <>
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-2" />
                  <h3 className="text-lg font-medium text-green-800">Validation Passed</h3>
                </>
              ) : (
                <>
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-500 mr-2" />
                  <h3 className="text-lg font-medium text-red-800">Validation Failed</h3>
                </>
              )}
            </div>
            
            <div className="space-y-2 text-sm">
              <p>Total rows: {validationResult.total_rows}</p>
              {validationResult.missing_columns?.length > 0 && (
                <p className="text-red-600">
                  Missing columns: {validationResult.missing_columns.join(', ')}
                </p>
              )}
              {validationResult.validation_errors?.map((error, index) => (
                <p key={index} className="text-red-600">{error}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Import Results */}
      {importResult && (
        <div className="card border-green-200">
          <div className="card-body">
            <div className="flex items-center mb-4">
              <CheckCircleIcon className="h-6 w-6 text-green-500 mr-2" />
              <h3 className="text-lg font-medium text-green-800">Import Complete</h3>
            </div>
            
            <div className="space-y-2">
              <p>Records imported: {importResult.imported}</p>
              <p>Total rows processed: {importResult.total_rows}</p>
              {importResult.errors?.length > 0 && (
                <div className="mt-4">
                  <p className="font-medium text-red-600">Errors:</p>
                  <ul className="list-disc list-inside text-sm text-red-600">
                    {importResult.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Web Scraping */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium">Web Scraping</h3>
        </div>
        <div className="card-body">
          <p className="text-sm text-gray-600 mb-4">
            Automatically scrape tax sale data from county websites
          </p>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <button
                onClick={() => scrapeMutation.mutate('collin')}
                disabled={scrapeMutation.isLoading || scrapingStatus.collin?.status === 'running'}
                className="btn-secondary w-full"
              >
                <ArrowPathIcon className={`h-4 w-4 mr-2 ${scrapingStatus.collin?.status === 'running' ? 'animate-spin' : ''}`} />
                Scrape Collin County
              </button>
              {scrapingStatus.collin && (
                <div className={`mt-2 p-3 rounded-md text-sm ${
                  scrapingStatus.collin.status === 'error' ? 'bg-red-50 text-red-800' :
                  scrapingStatus.collin.status === 'completed' ? 'bg-green-50 text-green-800' :
                  'bg-blue-50 text-blue-800'
                }`}>
                  <p className="font-medium">{scrapingStatus.collin.message}</p>
                  {scrapingStatus.collin.progress !== undefined && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span>Progress</span>
                        <span>{scrapingStatus.collin.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-tax-primary h-2 rounded-full transition-all"
                          style={{ width: `${scrapingStatus.collin.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {(scrapingStatus.collin.propertiesFound !== undefined || scrapingStatus.collin.salesFound !== undefined) && (
                    <p className="mt-2 text-xs">
                      Found: {scrapingStatus.collin.propertiesFound || 0} properties, {scrapingStatus.collin.salesFound || 0} sales
                    </p>
                  )}
                </div>
              )}
            </div>
            
            <div>
              <button
                onClick={() => scrapeMutation.mutate('dallas')}
                disabled={scrapeMutation.isLoading || scrapingStatus.dallas?.status === 'running'}
                className="btn-secondary w-full"
              >
                <ArrowPathIcon className={`h-4 w-4 mr-2 ${scrapingStatus.dallas?.status === 'running' ? 'animate-spin' : ''}`} />
                Scrape Dallas County
              </button>
              {scrapingStatus.dallas && (
                <div className={`mt-2 p-3 rounded-md text-sm ${
                  scrapingStatus.dallas.status === 'error' ? 'bg-red-50 text-red-800' :
                  scrapingStatus.dallas.status === 'completed' ? 'bg-green-50 text-green-800' :
                  'bg-blue-50 text-blue-800'
                }`}>
                  <p className="font-medium">{scrapingStatus.dallas.message}</p>
                  {scrapingStatus.dallas.progress !== undefined && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span>Progress</span>
                        <span>{scrapingStatus.dallas.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-tax-primary h-2 rounded-full transition-all"
                          style={{ width: `${scrapingStatus.dallas.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {(scrapingStatus.dallas.propertiesFound !== undefined || scrapingStatus.dallas.salesFound !== undefined) && (
                    <p className="mt-2 text-xs">
                      Found: {scrapingStatus.dallas.propertiesFound || 0} properties, {scrapingStatus.dallas.salesFound || 0} sales
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataImport;