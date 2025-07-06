import React, { useState, useRef, useEffect } from 'react';
import { Upload, Camera, FileText, Download, Settings, Edit2, Trash2, Plus, Check, X, AlertCircle, Loader } from 'lucide-react';
import { apiService } from './services/api';

const ReceiptFilingApp = () => {
  const [uploadedImages, setUploadedImages] = useState([]);
  const [extractedData, setExtractedData] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [categories, setCategories] = useState([]);
  const [showCategoryEditor, setShowCategoryEditor] = useState(false);
  const [newCategory, setNewCategory] = useState('');
  const [editingRow, setEditingRow] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [apiConnected, setApiConnected] = useState(false);
  const fileInputRef = useRef(null);

  // Test API connection and load categories on mount
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Test API connection
      await apiService.testConnection();
      setApiConnected(true);
      
      // Load categories
      const categoryData = await apiService.getCategories();
      // Convert backend categories to frontend format
      const categoryNames = Object.keys(categoryData);
      setCategories(categoryNames);
      setError(null);
    } catch (err) {
      setError(`Failed to connect to API: ${err.message}`);
      setApiConnected(false);
      // Fallback to default categories
      setCategories([
        'Food & Dining', 'Transportation', 'Shopping', 'Utilities', 
        'Healthcare', 'Entertainment', 'Office Supplies', 'Other'
      ]);
    }
  };

  const handleFileUpload = async (files) => {
    if (!apiConnected) {
      setError('API not connected. Please check your backend server.');
      return;
    }

    const fileArray = Array.from(files);
    setUploadedImages(fileArray);
    setProcessing(true);
    setError(null);
    setUploadProgress(0);

    try {
      console.log('Uploading files to API...');
      const results = await apiService.uploadReceipts(fileArray);
      
      // Process results and convert to frontend format
      const processedData = results.map((result, index) => {
        if (result.status === 'success' && result.data) {
          return {
            id: Date.now() + index, // Generate unique ID
            filename: result.filename,
            date: result.data.date ? result.data.date.split('T')[0] : new Date().toISOString().split('T')[0],
            merchant: result.data.merchant || 'Unknown',
            category: result.data.category || 'Other',
            amount: result.data.amount ? parseFloat(result.data.amount) : 0,
            currency: result.data.currency || 'NTD',
            confidence: result.data.confidence || 0,
            items: result.data.items || [],
            raw_text: result.data.raw_text || ''
          };
        } else {
          // Handle error results
          console.error(`Processing failed for ${result.filename}:`, result.error);
          return {
            id: Date.now() + index,
            filename: result.filename,
            date: new Date().toISOString().split('T')[0],
            merchant: 'Processing Failed',
            category: 'Other',
            amount: 0,
            currency: 'NTD',
            confidence: 0,
            error: result.error
          };
        }
      });

      setExtractedData(processedData);
      setProcessing(false);
      
      // Show any processing errors
      const errors = results.filter(r => r.status === 'error');
      if (errors.length > 0) {
        setError(`Some files failed to process: ${errors.map(e => e.filename).join(', ')}`);
      }
      
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
      setProcessing(false);
      console.error('Upload error:', err);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  const updateRow = (id, field, value) => {
    setExtractedData(prev => 
      prev.map(row => 
        row.id === id ? { ...row, [field]: value } : row
      )
    );
  };

  const deleteRow = (id) => {
    setExtractedData(prev => prev.filter(row => row.id !== id));
  };

  const addCategory = () => {
    if (newCategory.trim() && !categories.includes(newCategory.trim())) {
      setCategories(prev => [...prev, newCategory.trim()]);
      setNewCategory('');
    }
  };

  const removeCategory = (categoryToRemove) => {
    setCategories(prev => prev.filter(cat => cat !== categoryToRemove));
  };

  const exportToCSV = async () => {
    try {
      // Convert frontend data to backend format
      const receiptsData = extractedData.map(row => ({
        date: row.date,
        merchant: row.merchant,
        category: row.category,
        amount: row.amount,
        currency: row.currency,
        items: row.items || []
      }));

      await apiService.exportToCSV(receiptsData);
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };

  const exportToExcel = async () => {
    try {
      // Convert frontend data to backend format
      const receiptsData = extractedData.map(row => ({
        date: row.date,
        merchant: row.merchant,
        category: row.category,
        amount: row.amount,
        currency: row.currency,
        items: row.items || []
      }));

      await apiService.exportToExcel(receiptsData);
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };

  const copyToClipboard = () => {
    const tableData = extractedData.map(row => 
      `${row.date}\t${row.merchant}\t${row.category}\t${row.amount}\t${row.currency}`
    ).join('\n');
    
    navigator.clipboard.writeText(`Date\tMerchant\tCategory\tAmount\tCurrency\n${tableData}`);
    alert('Data copied to clipboard! You can paste it directly into Google Sheets.');
  };

  const dismissError = () => {
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Receipt Filing App</h1>
                <p className="text-gray-600">Extract expense data from receipt images with AI</p>
                <div className="flex items-center space-x-2 mt-1">
                  <div className={`w-2 h-2 rounded-full ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-500">
                    {apiConnected ? 'API Connected' : 'API Disconnected'}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowCategoryEditor(!showCategoryEditor)}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Settings className="w-4 h-4" />
              <span>Categories</span>
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
              <div className="flex-1">
                <h3 className="text-red-800 font-semibold">Error</h3>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
              <button
                onClick={dismissError}
                className="text-red-500 hover:text-red-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Category Editor */}
        {showCategoryEditor && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Manage Categories</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {categories.map((category, index) => (
                <div key={index} className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                  <span className="text-sm">{category}</span>
                  <button
                    onClick={() => removeCategory(category)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="Add new category"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && addCategory()}
              />
              <button
                onClick={addCategory}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-1"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>
          </div>
        )}

        {/* Upload Area */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Upload Receipt Images</h3>
                <p className="text-gray-600">Drag and drop images here, or click to select files</p>
                <p className="text-sm text-gray-500 mt-1">Supports JPG, PNG, WebP, HEIC (max 10MB each)</p>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {uploadedImages.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold text-gray-900 mb-2">Uploaded Images ({uploadedImages.length})</h4>
              <div className="flex flex-wrap gap-2">
                {uploadedImages.map((file, index) => (
                  <div key={index} className="bg-gray-100 px-3 py-1 rounded-lg text-sm">
                    {file.name}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Processing Indicator */}
        {processing && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center space-x-3">
              <Loader className="w-6 h-6 text-blue-600 animate-spin" />
              <div>
                <span className="text-gray-700 font-medium">Processing receipts with Google Cloud Vision AI...</span>
                <p className="text-sm text-gray-500">This may take 10-30 seconds depending on image complexity</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Table */}
        {extractedData.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Extracted Data</h3>
              <div className="flex space-x-2">
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>Copy for Sheets</span>
                </button>
                <button
                  onClick={exportToCSV}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Export CSV</span>
                </button>
                <button
                  onClick={exportToExcel}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Export Excel</span>
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left p-3 font-semibold text-gray-900">Date</th>
                    <th className="text-left p-3 font-semibold text-gray-900">Merchant</th>
                    <th className="text-left p-3 font-semibold text-gray-900">Category</th>
                    <th className="text-left p-3 font-semibold text-gray-900">Amount</th>
                    <th className="text-left p-3 font-semibold text-gray-900">Currency</th>
                    <th className="text-left p-3 font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {extractedData.map((row) => (
                    <tr key={row.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="p-3">
                        {editingRow === row.id ? (
                          <input
                            type="date"
                            value={row.date}
                            onChange={(e) => updateRow(row.id, 'date', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          />
                        ) : (
                          row.date
                        )}
                      </td>
                      <td className="p-3">
                        {editingRow === row.id ? (
                          <input
                            type="text"
                            value={row.merchant}
                            onChange={(e) => updateRow(row.id, 'merchant', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          />
                        ) : (
                          <div>
                            <div>{row.merchant}</div>
                            {row.error && (
                              <div className="text-xs text-red-500 mt-1">Error: {row.error}</div>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="p-3">
                        {editingRow === row.id ? (
                          <select
                            value={row.category}
                            onChange={(e) => updateRow(row.id, 'category', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          >
                            {categories.map(cat => (
                              <option key={cat} value={cat}>{cat}</option>
                            ))}
                          </select>
                        ) : (
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                            {row.category}
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        {editingRow === row.id ? (
                          <input
                            type="number"
                            value={row.amount}
                            onChange={(e) => updateRow(row.id, 'amount', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          />
                        ) : (
                          <div>
                            <div>{row.amount.toLocaleString()}</div>
                            {row.confidence > 0 && (
                              <div className="text-xs text-gray-500">
                                {row.confidence}% confidence
                              </div>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="p-3">
                        {editingRow === row.id ? (
                          <select
                            value={row.currency}
                            onChange={(e) => updateRow(row.id, 'currency', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          >
                            <option value="NTD">NTD (台幣)</option>
                            <option value="HKD">HKD (港幣)</option>
                            <option value="USD">USD (美金)</option>
                          </select>
                        ) : (
                          row.currency
                        )}
                      </td>
                      <td className="p-3">
                        <div className="flex space-x-2">
                          {editingRow === row.id ? (
                            <>
                              <button
                                onClick={() => setEditingRow(null)}
                                className="text-green-600 hover:text-green-800"
                                title="Save changes"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => setEditingRow(null)}
                                className="text-gray-600 hover:text-gray-800"
                                title="Cancel editing"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={() => setEditingRow(row.id)}
                                className="text-blue-600 hover:text-blue-800"
                                title="Edit row"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => deleteRow(row.id)}
                                className="text-red-600 hover:text-red-800"
                                title="Delete row"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 text-sm text-gray-600">
              <p>Total entries: {extractedData.length}</p>
              <p>Processed with Google Cloud Vision AI. Click the edit icon to modify any field, or use "Copy for Sheets" to paste directly into Google Sheets.</p>
            </div>
          </div>
        )}

        {/* Instructions */}
        {extractedData.length === 0 && !processing && (
          <div className="bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">How to use:</h3>
            <ol className="list-decimal list-inside space-y-2 text-blue-800">
              <li>Upload one or more receipt images using the upload area above</li>
              <li>Wait for the AI to process and extract expense information</li>
              <li>Review and edit the extracted data if needed</li>
              <li>Configure expense categories using the Categories button</li>
              <li>Export to CSV/Excel or copy the data to paste into Google Sheets</li>
            </ol>
            <div className="mt-4 p-3 bg-blue-100 rounded">
              <p className="text-sm text-blue-700">
                <strong>Powered by Google Cloud Vision AI</strong> for accurate text extraction from receipts in multiple languages.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReceiptFilingApp;