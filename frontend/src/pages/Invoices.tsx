import React, { useState, useEffect } from 'react';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

interface Invoice {
  id: number;
  filename: string;
  vendor_name?: string;
  total_amount?: number;
  upload_date: string;
  processing_status: string;
  parsed_data?: any;
}

const Invoices: React.FC = () => {
  const { user } = useAuth();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; invoiceId: number | null }>({
    isOpen: false,
    invoiceId: null
  });

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/invoices/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setInvoices(response.data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
      // Fall back to mock data if API fails
      setInvoices([
        {
          id: 1,
          filename: 'invoice_001.pdf',
          vendor_name: 'Fresh Foods Co.',
          total_amount: 234.50,
          upload_date: '2025-06-28T10:30:00Z',
          processing_status: 'completed',
          parsed_data: {
            categorized_items: {
              proteins: [
                { name: 'Chicken Breast', quantity: 5, unit: 'lb', price: 24.95 },
                { name: 'Salmon Fillet', quantity: 3, unit: 'lb', price: 32.40 }
              ],
              vegetables: [
                { name: 'Organic Tomatoes', quantity: 10, unit: 'lb', price: 18.50 },
                { name: 'Fresh Spinach', quantity: 2, unit: 'lb', price: 8.75 }
              ],
              dairy: [
                { name: 'Mozzarella Cheese', quantity: 2, unit: 'lb', price: 12.30 }
              ]
            }
          }
        },
        {
          id: 2,
          filename: 'invoice_002.pdf',
          vendor_name: 'Green Produce',
          total_amount: 156.75,
          upload_date: '2025-06-26T14:15:00Z',
          processing_status: 'completed'
        },
        {
          id: 3,
          filename: 'invoice_003.pdf',
          vendor_name: 'Meat Supply Inc.',
          total_amount: 412.30,
          upload_date: '2025-06-25T09:45:00Z',
          processing_status: 'processing'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (invoiceId: number) => {
    setDeleteConfirm({ isOpen: true, invoiceId });
  };

  const confirmDelete = async () => {
    if (deleteConfirm.invoiceId) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`/api/invoices/${deleteConfirm.invoiceId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setInvoices(prev => prev.filter(inv => inv.id !== deleteConfirm.invoiceId));
      } catch (error) {
        console.error('Failed to delete invoice:', error);
        // For now, still remove from UI even if API call fails
        setInvoices(prev => prev.filter(inv => inv.id !== deleteConfirm.invoiceId));
      }
    }
    setDeleteConfirm({ isOpen: false, invoiceId: null });
  };

  const cancelDelete = () => {
    setDeleteConfirm({ isOpen: false, invoiceId: null });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusStyles[status as keyof typeof statusStyles] || statusStyles.pending}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
        <p className="text-gray-600 mt-2">
          Manage and view your uploaded invoices and their processing status
        </p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  File
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Upload Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {invoice.filename}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {invoice.vendor_name || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {invoice.total_amount ? `$${invoice.total_amount.toFixed(2)}` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {formatDate(invoice.upload_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(invoice.processing_status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <button
                      onClick={() => setSelectedInvoice(invoice)}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(invoice.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {invoices.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl text-gray-400 mb-4">📄</div>
            <p className="text-gray-500">No invoices uploaded yet</p>
          </div>
        )}
      </div>

      {/* Invoice Detail Modal */}
      {selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Invoice Details
                </h2>
                <button
                  onClick={() => setSelectedInvoice(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Filename</label>
                  <p className="text-sm text-gray-900">{selectedInvoice.filename}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Vendor</label>
                  <p className="text-sm text-gray-900">{selectedInvoice.vendor_name || 'Not detected'}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Total Amount</label>
                  <p className="text-sm text-gray-900">
                    {selectedInvoice.total_amount ? `$${selectedInvoice.total_amount.toFixed(2)}` : 'Not detected'}
                  </p>
                </div>

                {selectedInvoice.parsed_data?.categorized_items && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Parsed Ingredients</label>
                    <div className="space-y-3">
                      {Object.entries(selectedInvoice.parsed_data.categorized_items).map(([category, items]: [string, any]) => (
                        <div key={category} className="border border-gray-200 rounded p-3">
                          <h4 className="font-medium text-gray-900 capitalize mb-2">{category}</h4>
                          <div className="space-y-1">
                            {items.map((item: any, index: number) => (
                              <div key={index} className="flex justify-between text-sm">
                                <span>{item.name}</span>
                                <span>{item.quantity} {item.unit} - ${item.price}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
        title="Delete Invoice"
        message="Are you sure you want to delete this invoice? This action cannot be undone."
      />
    </div>
  );
};

export default Invoices;
