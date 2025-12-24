import React, { useState, useEffect } from 'react';
import { BarChart3, Download, Users, MessageCircle, Activity } from 'lucide-react';
import { StatCard } from '../../components/admin/StatCard';
import { apiClient } from '../../api/client';

interface AnalyticsData {
  users: {
    total: number;
    registered: number;
    anonymous: number;
    new_this_week: number;
  };
  circles: {
    total: number;
  };
  posts: {
    total: number;
    flagged: number;
  };
  paths: {
    total: number;
    active_enrollments: number;
  };
  mood_tracking: {
    total_entries: number;
    avg_mood_this_week: number;
  };
  conversations: {
    total: number;
  };
}

export function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const analytics = await apiClient.adminGetAnalytics();
      setData(analytics);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading analytics...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-6xl mx-auto py-12 text-center">
        <p className="text-secondary">Failed to load analytics data</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-light text-primary">
            Analytics & Reporting
          </h2>
          <p className="text-secondary text-sm">
            Platform usage and health metrics.
          </p>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 border border-divider rounded-xl text-sm font-medium text-secondary hover:text-primary hover:bg-white transition-colors">
          <Download size={16} />
          <span>Export Report</span>
        </button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard 
          title="Total Users" 
          value={data.users.total.toString()} 
          change={0} 
          icon={Users} 
          color="blue" 
        />
        <StatCard 
          title="New This Week" 
          value={data.users.new_this_week.toString()} 
          change={0} 
          icon={Users} 
          color="sage" 
        />
        <StatCard 
          title="Total Circles" 
          value={data.circles.total.toString()} 
          change={0} 
          icon={MessageCircle} 
          color="orange" 
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Total Posts</div>
          <div className="text-2xl font-light text-primary">{data.posts.total}</div>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Flagged Posts</div>
          <div className="text-2xl font-light text-primary">{data.posts.flagged}</div>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Total Paths</div>
          <div className="text-2xl font-light text-primary">{data.paths.total}</div>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Active Enrollments</div>
          <div className="text-2xl font-light text-primary">{data.paths.active_enrollments}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Total Conversations</div>
          <div className="text-2xl font-light text-primary">{data.conversations.total}</div>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Mood Entries</div>
          <div className="text-2xl font-light text-primary">{data.mood_tracking.total_entries}</div>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="text-sm text-secondary mb-1">Avg Mood (Week)</div>
          <div className="text-2xl font-light text-primary">{data.mood_tracking.avg_mood_this_week}/10</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-8 shadow-sm border border-divider/50">
        <h3 className="text-lg font-medium text-primary mb-6">User Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-background rounded-xl">
            <div className="text-3xl font-light text-primary mb-2">{data.users.registered}</div>
            <div className="text-sm text-secondary">Registered Users</div>
            <div className="text-xs text-subtle mt-1">
              {((data.users.registered / data.users.total) * 100).toFixed(1)}% of total
            </div>
          </div>
          <div className="text-center p-6 bg-background rounded-xl">
            <div className="text-3xl font-light text-primary mb-2">{data.users.anonymous}</div>
            <div className="text-sm text-secondary">Anonymous Users</div>
            <div className="text-xs text-subtle mt-1">
              {((data.users.anonymous / data.users.total) * 100).toFixed(1)}% of total
            </div>
          </div>
          <div className="text-center p-6 bg-background rounded-xl">
            <div className="text-3xl font-light text-primary mb-2">{data.users.new_this_week}</div>
            <div className="text-sm text-secondary">New This Week</div>
            <div className="text-xs text-subtle mt-1">
              Growth indicator
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}