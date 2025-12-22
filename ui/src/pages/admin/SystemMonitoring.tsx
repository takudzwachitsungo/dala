import React from 'react';
import { Activity, Cpu, Server, AlertCircle } from 'lucide-react';
import { StatCard } from '../../components/admin/StatCard';
export function SystemMonitoring() {
  return <div className="max-w-6xl mx-auto space-y-8">
      <header className="mb-8">
        <h2 className="text-2xl font-light text-primary">System Monitoring</h2>
        <p className="text-secondary text-sm">
          AI performance and system health.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="AI Response Time" value="1.2s" change={-5} icon={Cpu} color="blue" />
        <StatCard title="Error Rate" value="0.02%" change={-10} icon={AlertCircle} color="sage" />
        <StatCard title="Active Sessions" value="124" change={8} icon={Server} color="orange" />
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
            Recent System Logs
          </h3>
          <div className="space-y-3">
            {[1, 2, 3].map(i => <div key={i} className="flex items-start space-x-3 text-sm">
                <span className="text-secondary font-mono text-xs mt-0.5">
                  10:4{i} AM
                </span>
                <span className="text-primary">
                  Model response generated successfully for session #{1000 + i}
                </span>
              </div>)}
          </div>
        </div>
      </div>
    </div>;
}