import React, { useState, useEffect } from 'react';
import { Activity, Cpu, Server, AlertCircle, MessageSquare, Flag } from 'lucide-react';
import { StatCard } from '../../components/admin/StatCard';
import { apiClient } from '../../api/client';

interface ModerationSummary {
  total_flagged_posts: number;
  pending_review: number;
  actioned_today: number;
  high_severity_count: number;
}

export function SystemMonitoring() {
  const [summary, setSummary] = useState<ModerationSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await apiClient.adminGetModerationSummary();
      setSummary(data);
    } catch (error) {
      console.error('Failed to load moderation summary:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading system status...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header className="mb-8">
        <h2 className="text-2xl font-light text-primary">System Monitoring</h2>
        <p className="text-secondary text-sm">
          AI performance and system health.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard 
          title="Flagged Posts" 
          value={summary?.total_flagged_posts.toString() || '0'} 
          change={0} 
          icon={Flag} 
          color="orange" 
        />
        <StatCard 
          title="Pending Review" 
          value={summary?.pending_review.toString() || '0'} 
          change={0} 
          icon={AlertCircle} 
          color="blue" 
        />
        <StatCard 
          title="Actioned Today" 
          value={summary?.actioned_today.toString() || '0'} 
          change={0} 
          icon={Activity} 
          color="sage" 
        />
        <StatCard 
          title="High Severity" 
          value={summary?.high_severity_count.toString() || '0'} 
          change={0} 
          icon={AlertCircle} 
          color="red" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <h3 className="text-lg font-medium text-primary mb-4">
            Model Status
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-background rounded-xl">
              <div>
                <p className="text-sm font-medium text-primary">
                  Current Model
                </p>
                <p className="text-xs text-secondary">Dala-v2.4 (Fine-tuned)</p>
              </div>
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                Active
              </span>
            </div>
            <div className="flex justify-between items-center p-4 bg-background rounded-xl">
              <div>
                <p className="text-sm font-medium text-primary">
                  Safety Filter
                </p>
                <p className="text-xs text-secondary">Strict Mode Enabled</p>
              </div>
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                Operational
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <h3 className="text-lg font-medium text-primary mb-4">
            Moderation Activity
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-background rounded-xl">
              <div>
                <p className="text-sm font-medium text-primary">Total Flagged</p>
                <p className="text-xs text-secondary">All-time flagged posts</p>
              </div>
              <span className="text-2xl font-light text-primary">
                {summary?.total_flagged_posts || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-4 bg-background rounded-xl">
              <div>
                <p className="text-sm font-medium text-primary">Pending Review</p>
                <p className="text-xs text-secondary">Awaiting action</p>
              </div>
              <span className="text-2xl font-light text-orange-600">
                {summary?.pending_review || 0}
              </span>
            </div>
            <div className="flex justify-between items-center p-4 bg-background rounded-xl">
              <div>
                <p className="text-sm font-medium text-primary">High Severity</p>
                <p className="text-xs text-secondary">Critical items</p>
              </div>
              <span className="text-2xl font-light text-red-600">
                {summary?.high_severity_count || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}