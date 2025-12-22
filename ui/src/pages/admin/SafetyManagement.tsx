import React, { useState, useEffect } from 'react';
import { AlertTriangle, Clock, ChevronRight } from 'lucide-react';
import { apiClient } from '../../api/client';

interface AtRiskUser {
  id: string;
  username: string;
  risk_level: string;
  escalation_status: string;
  last_risk_assessment: string;
  is_anonymous: boolean;
}

export function SafetyManagement() {
  const [users, setUsers] = useState<AtRiskUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'critical' | 'high'>('all');
  const [selectedUser, setSelectedUser] = useState<AtRiskUser | null>(null);

  useEffect(() => {
    loadAtRiskUsers();
  }, [filter]);

  const loadAtRiskUsers = async () => {
    try {
      setLoading(true);
      const riskLevel = filter === 'all' ? 'high' : filter;
      const data = await apiClient.adminGetAtRiskUsers(riskLevel, 0, 50);
      setUsers(data);
    } catch (error) {
      console.error('Failed to load at-risk users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEscalate = async (userId: string, status: string) => {
    try {
      await apiClient.adminUpdateEscalationStatus(userId, status);
      loadAtRiskUsers();
      setSelectedUser(null);
    } catch (error) {
      console.error('Failed to update escalation:', error);
      alert('Failed to update escalation status');
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading safety dashboard...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-light text-primary mb-2">Safety Management</h2>
        <p className="text-secondary text-sm">Monitor and support users with elevated risk indicators</p>
      </header>

      {/* Risk Level Filter */}
      <div className="mb-6 flex items-center space-x-2">
        <span className="text-xs text-secondary mr-2">Filter by risk:</span>
        {(['all', 'critical', 'high'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-sm font-medium capitalize transition-colors ${
              filter === f
                ? 'bg-primary text-white'
                : 'bg-white border border-divider text-secondary hover:border-primary'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Crisis Resources Banner */}
      <div className="mb-6 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 border border-red-200">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-red-100 rounded-xl">
            <AlertTriangle className="text-red-600" size={24} />
          </div>
          <div className="flex-1">
            <h3 className="font-medium text-primary mb-2">Crisis Resources</h3>
            <div className="text-sm text-secondary space-y-1">
              <p>🇺🇸 <strong>Crisis Line:</strong> 988 (call or text)</p>
              <p>💬 <strong>Crisis Text:</strong> Text HOME to 741741</p>
              <p>🌍 <strong>International:</strong> findahelpline.com</p>
              <p>🚨 <strong>Emergency:</strong> 911 or local emergency services</p>
            </div>
          </div>
        </div>
      </div>

      {/* At-Risk Users List */}
      {users.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-divider">
          <p className="text-secondary">No users currently flagged at this risk level</p>
          <p className="text-xs text-secondary mt-2">This is good news! ✨</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {users.map((user) => (
            <div
              key={user.id}
              className="bg-white rounded-xl p-6 border border-divider hover:border-sage/50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="font-medium text-primary">
                      {user.username}
                      {user.is_anonymous && (
                        <span className="ml-2 text-xs text-secondary">(Anonymous User)</span>
                      )}
                    </h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(
                        user.risk_level
                      )}`}
                    >
                      {user.risk_level.toUpperCase()} RISK
                    </span>
                    {user.escalation_status && (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 border border-purple-300">
                        {user.escalation_status}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-4 text-xs text-secondary">
                    <span className="flex items-center">
                      <Clock size={12} className="mr-1" />
                      Last assessed: {new Date(user.last_risk_assessment).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  {!user.escalation_status || user.escalation_status === 'pending' ? (
                    <button
                      onClick={() => handleEscalate(user.id, 'escalated')}
                      className="px-4 py-2 rounded-xl bg-orange-500 text-white hover:bg-orange-600 transition-colors text-sm"
                    >
                      Escalate to Support
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEscalate(user.id, 'resolved')}
                      className="px-4 py-2 rounded-xl bg-green-500 text-white hover:bg-green-600 transition-colors text-sm"
                    >
                      Mark Resolved
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedUser(user)}
                    className="p-2 rounded-xl border border-divider hover:border-sage transition-colors"
                  >
                    <ChevronRight size={20} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* User Detail Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-medium text-primary">User Risk Profile</h3>
              <button
                onClick={() => setSelectedUser(null)}
                className="p-2 hover:bg-background rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-primary mb-1">Username</label>
                <p className="text-secondary">{selectedUser.username}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-primary mb-1">Risk Level</label>
                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(
                    selectedUser.risk_level
                  )}`}
                >
                  {selectedUser.risk_level.toUpperCase()}
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-primary mb-1">
                  Escalation Status
                </label>
                <p className="text-secondary">{selectedUser.escalation_status || 'None'}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-primary mb-1">
                  Last Assessment
                </label>
                <p className="text-secondary">
                  {new Date(selectedUser.last_risk_assessment).toLocaleString()}
                </p>
              </div>

              <div className="pt-4 border-t border-divider">
                <p className="text-xs text-secondary">
                  <strong>Important:</strong> Always follow your organization's crisis intervention
                  protocols. If immediate danger is suspected, contact emergency services.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}