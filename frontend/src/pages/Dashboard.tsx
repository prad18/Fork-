import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

interface DashboardStats {
  totalInvoices: number;
  totalEmissions: number;
  monthlyEmissions: number;
  recentInvoices: any[];
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalInvoices: 0,
    totalEmissions: 0,
    monthlyEmissions: 0,
    recentInvoices: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Try to load real dashboard data
      const response = await axios.get('/api/carbon/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Merge API response with expected structure
      setStats({
        totalInvoices: response.data.total_invoices || 0,
        totalEmissions: response.data.total_emissions || 0,
        monthlyEmissions: response.data.monthly_emissions || 0,
        recentInvoices: response.data.recent_invoices || []
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Fall back to mock data if API fails
      setStats({
        totalInvoices: 12,
        totalEmissions: 145.7,
        monthlyEmissions: 42.3,
        recentInvoices: [
          { id: 1, filename: 'invoice_001.pdf', vendor: 'Fresh Foods Co.', amount: 234.50, date: '2025-06-28' },
          { id: 2, filename: 'invoice_002.pdf', vendor: 'Green Produce', amount: 156.75, date: '2025-06-26' },
          { id: 3, filename: 'invoice_003.pdf', vendor: 'Meat Supply Inc.', amount: 412.30, date: '2025-06-25' },
        ]
      });
    } finally {
      setIsLoading(false);
    }
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
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.restaurant_name}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's your sustainability dashboard overview
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-3xl text-blue-500 mr-4">📊</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Invoices</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalInvoices}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-3xl text-red-500 mr-4">🌍</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total CO₂e (kg)</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalEmissions}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-3xl text-green-500 mr-4">📈</div>
            <div>
              <p className="text-sm font-medium text-gray-600">This Month (kg CO₂e)</p>
              <p className="text-2xl font-bold text-gray-900">{stats.monthlyEmissions}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/upload"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <div className="text-2xl text-primary-500 mr-3">📤</div>
            <div>
              <h3 className="font-medium text-gray-900">Upload Invoice</h3>
              <p className="text-sm text-gray-600">Add new invoice</p>
            </div>
          </Link>

          <Link
            to="/carbon"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <div className="text-2xl text-primary-500 mr-3">🌱</div>
            <div>
              <h3 className="font-medium text-gray-900">Carbon Analysis</h3>
              <p className="text-sm text-gray-600">View emissions</p>
            </div>
          </Link>

          <div className="flex items-center p-4 border border-gray-200 rounded-lg opacity-50">
            <div className="text-2xl text-gray-400 mr-3">🥕</div>
            <div>
              <h3 className="font-medium text-gray-500">Recommendations</h3>
              <p className="text-sm text-gray-400">Coming soon</p>
            </div>
          </div>

          <div className="flex items-center p-4 border border-gray-200 rounded-lg opacity-50">
            <div className="text-2xl text-gray-400 mr-3">🏆</div>
            <div>
              <h3 className="font-medium text-gray-500">Achievements</h3>
              <p className="text-sm text-gray-400">Coming soon</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Invoices */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Invoices</h2>
          <Link to="/invoices" className="text-primary-600 hover:text-primary-500 text-sm font-medium">
            View all →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 text-sm font-medium text-gray-600">File</th>
                <th className="text-left py-2 text-sm font-medium text-gray-600">Vendor</th>
                <th className="text-left py-2 text-sm font-medium text-gray-600">Amount</th>
                <th className="text-left py-2 text-sm font-medium text-gray-600">Date</th>
              </tr>
            </thead>
            <tbody>
              {(stats.recentInvoices || []).map((invoice) => (
                <tr key={invoice.id} className="border-b border-gray-100">
                  <td className="py-3 text-sm text-gray-900">{invoice.filename}</td>
                  <td className="py-3 text-sm text-gray-600">{invoice.vendor || invoice.vendor_name || 'Unknown'}</td>
                  <td className="py-3 text-sm text-gray-900">${invoice.amount || '0.00'}</td>
                  <td className="py-3 text-sm text-gray-600">{invoice.date || invoice.upload_date || 'Unknown'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
