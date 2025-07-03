import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

interface CarbonDashboard {
  total_emissions: number;
  total_invoices: number;
  sustainability_score: number;
  emissions_by_category: { [key: string]: number };
  recent_invoices: Array<{
    id: number;
    filename: string;
    vendor_name: string;
    total_emissions: number;
    sustainability_score: number;
    upload_date: string;
  }>;
  recommendations: Array<{
    type: string;
    current_item?: string;
    recommendation: string;
    potential_reduction: string;
    priority: string;
  }>;
}

const CarbonFootprint: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<CarbonDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/carbon/dashboard');
      setDashboardData(response.data);
    } catch (error: any) {
      console.error('Failed to load carbon dashboard:', error);
      setError('Failed to load carbon footprint data');
      // Fallback to demo data
      setDashboardData({
        total_emissions: 73.6,
        total_invoices: 5,
        sustainability_score: 68,
        emissions_by_category: {
          protein: 42.8,
          dairy: 15.2,
          vegetables: 8.5,
          grains: 4.1,
          other: 3.0
        },
        recent_invoices: [
          {
            id: 1,
            filename: 'invoice_001.pdf',
            vendor_name: 'Fresh Foods Co.',
            total_emissions: 18.5,
            sustainability_score: 72,
            upload_date: new Date().toISOString()
          }
        ],
        recommendations: [
          {
            type: 'substitution',
            current_item: 'Beef',
            recommendation: 'Consider chicken, turkey, or plant-based alternatives',
            potential_reduction: '25.2 kg CO2e',
            priority: 'high'
          }
        ]
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Prepare chart data
  const categoryData = dashboardData ? Object.entries(dashboardData.emissions_by_category).map(([category, emissions]) => ({
    category: category.charAt(0).toUpperCase() + category.slice(1),
    emissions: Number(emissions.toFixed(1))
  })) : [];

  const pieData = dashboardData ? Object.entries(dashboardData.emissions_by_category).map(([category, emissions]) => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    value: Number(emissions.toFixed(1))
  })) : [];

  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

  const getSustainabilityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSustainabilityBadge = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading carbon footprint data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Carbon Footprint Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Track your restaurant's environmental impact and find ways to reduce emissions
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-yellow-400">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Demo Mode</h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>{error}. Showing demo data for preview.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {dashboardData && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">🌍</span>
                  </div>
                  <div className="ml-3 w-0 flex-1">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Emissions
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {dashboardData.total_emissions.toFixed(1)} kg CO₂e
                    </dd>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">📄</span>
                  </div>
                  <div className="ml-3 w-0 flex-1">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Processed Invoices
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {dashboardData.total_invoices}
                    </dd>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">🏆</span>
                  </div>
                  <div className="ml-3 w-0 flex-1">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Sustainability Score
                    </dt>
                    <dd className={`text-lg font-semibold ${getSustainabilityColor(dashboardData.sustainability_score)}`}>
                      {dashboardData.sustainability_score}/100
                    </dd>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">
                      {dashboardData.sustainability_score >= 80 ? '🌟' : 
                       dashboardData.sustainability_score >= 60 ? '✨' : '🔄'}
                    </span>
                  </div>
                  <div className="ml-3 w-0 flex-1">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Rating
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {getSustainabilityBadge(dashboardData.sustainability_score)}
                    </dd>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Category Breakdown - Bar Chart */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Emissions by Category</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categoryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value} kg CO₂e`, 'Emissions']} />
                    <Bar dataKey="emissions" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Category Breakdown - Pie Chart */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Emissions Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    >
                      {pieData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value} kg CO₂e`, 'Emissions']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Recommendations */}
            {dashboardData.recommendations.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Sustainability Recommendations</h3>
                <div className="space-y-4">
                  {dashboardData.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900">
                            {rec.current_item && `Replace ${rec.current_item}`}
                          </h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                            rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {rec.priority} priority
                          </span>
                        </div>
                        <p className="text-gray-600 mt-1">{rec.recommendation}</p>
                        <p className="text-sm text-green-600 mt-1">
                          Potential reduction: {rec.potential_reduction}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Invoices */}
            {dashboardData.recent_invoices.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Invoice Analysis</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Invoice
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Vendor
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Emissions
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Score
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {dashboardData.recent_invoices.map((invoice) => (
                        <tr key={invoice.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {invoice.filename}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {invoice.vendor_name || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {invoice.total_emissions.toFixed(1)} kg CO₂e
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSustainabilityColor(invoice.sustainability_score)} bg-gray-100`}>
                              {invoice.sustainability_score}/100
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(invoice.upload_date).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default CarbonFootprint;
