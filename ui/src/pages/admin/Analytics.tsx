import React from 'react';
import { BarChart3, Download } from 'lucide-react';
import { StatCard } from '../../components/admin/StatCard';
export function Analytics() {
  return <div className="max-w-6xl mx-auto space-y-8">
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
        <StatCard title="Daily Active Users" value="342" change={12} icon={BarChart3} color="blue" />
        <StatCard title="Weekly Retention" value="68%" change={2} icon={BarChart3} color="sage" />
        <StatCard title="Avg Session Time" value="8m 42s" change={-1} icon={BarChart3} color="orange" />
      </div>

      <div className="bg-white rounded-2xl p-8 shadow-sm border border-divider/50 flex items-center justify-center h-96">
        <div className="text-center">
          <BarChart3 size={48} className="mx-auto text-divider mb-4" />
          <p className="text-secondary">Chart visualization placeholder</p>
          <p className="text-xs text-subtle mt-1">
            (Requires charting library)
          </p>
        </div>
      </div>
    </div>;
}