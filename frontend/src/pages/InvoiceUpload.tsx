import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

interface UploadedFile {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  result?: any;
  error?: string;
}

const InvoiceUpload: React.FC = () => {
  const { user } = useAuth();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (!user) {
      alert('Please log in to upload invoices.');
      return;
    }

    acceptedFiles.forEach((file) => {
      const uploadedFile: UploadedFile = {
        file,
        progress: 0,
        status: 'uploading'
      };

      setUploadedFiles(prev => [...prev, uploadedFile]);
      uploadFile(file, uploadedFiles.length);
    });
  }, [uploadedFiles.length, user]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp'],
      'application/pdf': ['.pdf']
    },
    multiple: true,
    maxSize: 16 * 1024 * 1024 // 16MB
  });

  // Don't allow uploads if not authenticated
  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Please log in to upload invoices.</p>
      </div>
    );
  }

  const uploadFile = async (file: File, index: number) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/invoices/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent: any) => {
          const progress = progressEvent.total 
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          
          setUploadedFiles(prev => 
            prev.map((item, i) => 
              i === index ? { ...item, progress } : item
            )
          );
        },
      });

      // Update status to processing
      setUploadedFiles(prev => 
        prev.map((item, i) => 
          i === index ? { ...item, status: 'processing' } : item
        )
      );

      // Poll for processing completion
      pollProcessingStatus(response.data.id, index);

    } catch (error: any) {
      setUploadedFiles(prev => 
        prev.map((item, i) => 
          i === index ? { 
            ...item, 
            status: 'error', 
            error: error.response?.data?.detail || 'Upload failed' 
          } : item
        )
      );
    }
  };

  const pollProcessingStatus = async (invoiceId: number, index: number) => {
    try {
      const response = await axios.get(`/api/invoices/${invoiceId}`);
      
      if (response.data.processing_status === 'completed') {
        setUploadedFiles(prev => 
          prev.map((item, i) => 
            i === index ? { 
              ...item, 
              status: 'completed', 
              result: response.data 
            } : item
          )
        );
      } else if (response.data.processing_status === 'failed') {
        setUploadedFiles(prev => 
          prev.map((item, i) => 
            i === index ? { 
              ...item, 
              status: 'error', 
              error: 'Processing failed' 
            } : item
          )
        );
      } else {
        // Continue polling
        setTimeout(() => pollProcessingStatus(invoiceId, index), 2000);
      }
    } catch (error) {
      setUploadedFiles(prev => 
        prev.map((item, i) => 
          i === index ? { 
            ...item, 
            status: 'error', 
            error: 'Processing failed' 
          } : item
        )
      );
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploading': return 'blue';
      case 'processing': return 'yellow';
      case 'completed': return 'green';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'uploading': return 'Uploading...';
      case 'processing': return 'Processing...';
      case 'completed': return 'Completed';
      case 'error': return 'Error';
      default: return 'Unknown';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Invoice</h1>
        <p className="text-gray-600 mt-2">
          Upload your restaurant invoices for AI-powered sustainability analysis
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <div className="mx-auto h-16 w-16 text-gray-400">
            <svg
              className="h-full w-full"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <div>
            <p className="text-xl font-medium text-gray-900">
              {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-gray-500">
              or <span className="text-primary-600 font-medium">browse</span> to choose files
            </p>
            <p className="text-sm text-gray-400 mt-2">
              Supports PDF, PNG, JPG, JPEG, TIFF, BMP (max 16MB)
            </p>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Upload Progress</h3>
          {uploadedFiles.map((uploadedFile, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{uploadedFile.file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-medium rounded-full bg-${getStatusColor(
                        uploadedFile.status
                      )}-100 text-${getStatusColor(uploadedFile.status)}-800`}
                    >
                      {getStatusText(uploadedFile.status)}
                    </span>
                    {uploadedFile.status === 'uploading' && (
                      <span className="text-sm text-gray-500">
                        {uploadedFile.progress}%
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Progress Bar */}
              {uploadedFile.status === 'uploading' && (
                <div className="mt-2">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadedFile.progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Error Message */}
              {uploadedFile.status === 'error' && uploadedFile.error && (
                <div className="mt-2 text-sm text-red-600">
                  {uploadedFile.error}
                </div>
              )}

              {/* Success Message */}
              {uploadedFile.status === 'completed' && (
                <div className="mt-2 text-sm text-green-600">
                  Invoice processed successfully! 
                  {uploadedFile.result && (
                    <span className="ml-1">
                      - {uploadedFile.result.parsed_data?.items?.length || 0} items found
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InvoiceUpload;
