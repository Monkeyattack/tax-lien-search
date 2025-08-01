import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import api from '../services/authService';
import {
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  BellIcon,
  TrendingUpIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const { data: summary, isLoading: summaryLoading } = useQuery(
    'investment-summary',
    () => api.get('/investments/dashboard/summary').then(res => res.data)
  );

  const { data: alerts } = useQuery(
    'upcoming-alerts',
    () => api.get('/alerts/upcoming/summary').then(res => res.data)
  );

  const { data: recentInvestments } = useQuery(
    'recent-investments',
    () => api.get('/investments?limit=5').then(res => res.data)
  );

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tax-secondary"></div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Invested',
      value: summary ? `$${summary.total_invested.toLocaleString()}` : '$0',
      icon: CurrencyDollarIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Investments',
      value: summary?.active_investments || 0,
      icon: BuildingOfficeIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Total Profit',
      value: summary ? `$${summary.total_profit.toLocaleString()}` : '$0',
      icon: TrendingUpIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Avg ROI',
      value: summary ? `${summary.overall_roi_percent.toFixed(1)}%` : '0%',
      icon: TrendingUpIcon,
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your tax lien investments
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="card-body">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`p-3 rounded-md ${stat.color}`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-lg font-semibold text-gray-900">
                        {stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Alerts Section */}
      {alerts && alerts.urgent_alerts > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Urgent Alerts
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  You have {alerts.urgent_alerts} urgent alert{alerts.urgent_alerts !== 1 ? 's' : ''} 
                  requiring attention within the next 7 days.
                </p>
              </div>
              <div className="mt-4">
                <Link
                  to="/alerts"
                  className="text-sm font-medium text-yellow-800 hover:text-yellow-600"
                >
                  View all alerts →
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Investments */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <BuildingOfficeIcon className="h-5 w-5 mr-2" />
              Recent Investments
            </h3>
          </div>
          <div className="card-body">
            {recentInvestments && recentInvestments.length > 0 ? (
              <div className="space-y-4">
                {recentInvestments.map((investment) => (
                  <div key={investment.id} className="flex items-center justify-between py-2 border-b border-gray-200 last:border-b-0">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        Investment #{investment.id}
                      </p>
                      <p className="text-sm text-gray-500">
                        ${investment.purchase_amount.toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-900">
                        {investment.days_until_redemption !== null 
                          ? `${investment.days_until_redemption} days left`
                          : 'Expired'
                        }
                      </p>
                      <span className={`badge ${
                        investment.investment_status === 'active' 
                          ? 'badge-success' 
                          : investment.investment_status === 'redeemed'
                          ? 'badge-info'
                          : 'badge-warning'
                      }`}>
                        {investment.investment_status}
                      </span>
                    </div>
                  </div>
                ))}
                <div className="pt-2">
                  <Link
                    to="/investments"
                    className="text-sm font-medium text-tax-secondary hover:text-tax-secondary/80"
                  >
                    View all investments →
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No investments yet
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Start by exploring available properties
                </p>
                <div className="mt-6">
                  <Link
                    to="/properties"
                    className="btn-primary"
                  >
                    Browse Properties
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Upcoming Alerts */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <BellIcon className="h-5 w-5 mr-2" />
              Upcoming Alerts
            </h3>
          </div>
          <div className="card-body">
            {alerts && alerts.total_upcoming_alerts > 0 ? (
              <div className="space-y-4">
                {Object.entries(alerts.alert_types).map(([type, data]) => (
                  <div key={type} className="flex items-center justify-between py-2 border-b border-gray-200 last:border-b-0">
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 capitalize">
                          {type.replace('_', ' ')}
                        </p>
                        <p className="text-sm text-gray-500">
                          {data.count} alert{data.count !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    {data.urgent_count > 0 && (
                      <span className="badge badge-danger">
                        {data.urgent_count} urgent
                      </span>
                    )}
                  </div>
                ))}
                <div className="pt-2">
                  <Link
                    to="/alerts"
                    className="text-sm font-medium text-tax-secondary hover:text-tax-secondary/80"
                  >
                    View all alerts →
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No upcoming alerts
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  You're all caught up!
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link
              to="/properties"
              className="btn-secondary justify-center"
            >
              Browse Properties
            </Link>
            <Link
              to="/investments"
              className="btn-secondary justify-center"
            >
              Manage Investments
            </Link>
            <Link
              to="/counties"
              className="btn-secondary justify-center"
            >
              County Information
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;