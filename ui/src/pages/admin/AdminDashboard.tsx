import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, MessageSquare, ShieldAlert, HeartPulse, ArrowRight } from 'lucide-react';
import { StatCard } from '../../components/admin/StatCard';
import { apiClient } from '../../api/client';

interface AdminDashboardProps {
  onNavigate: (page: string) => void;
}

interface ModerationSummary {
  flagged_posts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  at_risk_users: {
    critical: number;
    high: number;
    total: number;
  };
  pending_escalations: number;
}

export function AdminDashboard({
  onNavigate
}: AdminDashboardProps) {
  const [summary, setSummary] = useState<ModerationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [recentFlags, setRecentFlags] = useState<any[]>([]);

  useEffect(() => {
    loadSummary();
    loadRecentFlags();
  }, []);

  const loadSummary = async () => {
    try {
      const data = await apiClient.adminGetModerationSummary();
      setSummary(data);
    } catch (error) {
      console.error('Failed to load moderation summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecentFlags = async () => {
    try {
      const data = await apiClient.adminGetFlaggedPosts(undefined, 0, 5);
      setRecentFlags(data.posts || []);
    } catch (error) {
      console.error('Failed to load recent flags:', error);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading dashboard...</p>
      </div>
    );
  }

  const totalFlagged = summary?.flagged_posts?.total || 0;
  const criticalPosts = summary?.flagged_posts?.critical || 0;
  const highRiskUsers = summary?.at_risk_users?.total || 0;
  const pendingEscalations = summary?.pending_escalations || 0;

  return <div className="max-w-6xl mx-auto space-y-8">
      <header className="mb-8">
        <h2 className="text-2xl font-light text-primary">Overview</h2>
        <p className="text-secondary text-sm">Platform health at a glance.</p>
      </header>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Flagged Posts" 
          value={totalFlagged.toString()} 
          change={criticalPosts > 0 ? criticalPosts : 0} 
          icon={ShieldAlert} 
          color="orange" 
        />
        <StatCard 
          title="High-Risk Users" 
          value={highRiskUsers.toString()} 
          change={summary?.at_risk_users?.critical || 0} 
          icon={HeartPulse} 
          color="red" 
        />
        <StatCard 
          title="Pending Escalations" 
          value={pendingEscalations.toString()} 
          change={0} 
          icon={MessageSquare} 
          color="sage" 
        />
        <StatCard 
          title="Critical Items" 
          value={(criticalPosts + (summary?.at_risk_users?.critical || 0)).toString()} 
          change={0} 
          icon={Users} 
          color="blue" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <h3 className="text-lg font-medium text-primary mb-6">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button onClick={() => onNavigate('moderation')} className="flex items-center justify-between p-4 rounded-xl bg-orange-50 border border-orange-100 hover:bg-orange-100 transition-colors text-left group">
              <div>
                <span className="block font-medium text-orange-900">
                  Review Flagged Content
                </span>
                <span className="text-xs text-orange-700">
                  {totalFlagged} item{totalFlagged !== 1 ? 's' : ''} pending
                </span>
              </div>
              <ArrowRight size={18} className="text-orange-400 group-hover:translate-x-1 transition-transform" />
            </button>

            <button onClick={() => onNavigate('safety')} className="flex items-center justify-between p-4 rounded-xl bg-red-50 border border-red-100 hover:bg-red-100 transition-colors text-left group">
              <div>
                <span className="block font-medium text-red-900">
                  Respond to Alerts
                </span>
                <span className="text-xs text-red-700">
                  {highRiskUsers} high-risk case{highRiskUsers !== 1 ? 's' : ''}
                </span>
              </div>
              <ArrowRight size={18} className="text-red-400 group-hover:translate-x-1 transition-transform" />
            </button>

            <button onClick={() => onNavigate('circles')} className="flex items-center justify-between p-4 rounded-xl bg-sage/5 border border-sage/20 hover:bg-sage/10 transition-colors text-left group">
              <div>
                <span className="block font-medium text-primary">
                  Manage Circles
                </span>
                <span className="text-xs text-secondary">
                  Update guidelines
                </span>
              </div>
              <ArrowRight size={18} className="text-sage group-hover:translate-x-1 transition-transform" />
            </button>

            <button onClick={() => onNavigate('users')} className="flex items-center justify-between p-4 rounded-xl bg-white border border-divider hover:border-sage/50 transition-colors text-left group">
              <div>
                <span className="block font-medium text-primary">
                  User Search
                </span>
                <span className="text-xs text-secondary">Find by nickname</span>
              </div>
              <ArrowRight size={18} className="text-secondary group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-primary">Recent Flags</h3>
            <button onClick={() => onNavigate('moderation')} className="text-xs text-sage font-medium hover:underline">
              View All
            </button>
          </div>

          <div className="space-y-4">
            {recentFlags.length === 0 ? (
              <div className="text-center py-6 text-secondary text-sm">
                No flagged content
              </div>
            ) : (
              recentFlags.map(flag => <div key={flag.id} className="flex items-start space-x-3 p-3 rounded-xl hover:bg-background transition-colors">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    flag.severity === 'critical' || flag.severity === 'high' 
                      ? 'bg-red-500' 
                      : flag.severity === 'medium' 
                        ? 'bg-orange-500' 
                        : 'bg-yellow-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-primary">
                      {flag.flag_reason || 'Flagged content'}
                    </p>
                    <p className="text-xs text-secondary">
                      {new Date(flag.flagged_at || flag.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>)
            )}
          </div>
        </div>
      </div>
    </div>;
}