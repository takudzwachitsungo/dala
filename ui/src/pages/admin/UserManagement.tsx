import React, { useState, useEffect } from 'react';
import { Search, MoreHorizontal, Shield, Ban, Eye } from 'lucide-react';
import { apiClient } from '../../api/client';

interface User {
  id: string;
  username: string;
  email?: string;
  role: string;
  is_active: boolean;
  is_admin: boolean;
  is_moderator: boolean;
  is_anonymous: boolean;
  risk_level: string;
  escalation_status?: string;
  created_at: string;
  flag_count: number;
}

export function UserManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await apiClient.adminGetUsers(searchTerm || undefined, 0, 50);
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadUsers();
  };

  const handleChangeRole = async (userId: string, newRole: string) => {
    try {
      setActionLoading(userId);
      await apiClient.adminUpdateUserRole(userId, newRole);
      await loadUsers(); // Refresh
    } catch (error) {
      console.error('Failed to change role:', error);
      alert('Failed to change user role');
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuspendUser = async (userId: string) => {
    if (!confirm('Are you sure you want to suspend this user?')) return;
    
    try {
      setActionLoading(userId);
      await apiClient.adminUpdateUserRole(userId, 'suspended');
      await loadUsers(); // Refresh
    } catch (error) {
      console.error('Failed to suspend user:', error);
      alert('Failed to suspend user');
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getStatusFromUser = (user: User): { status: string; color: string } => {
    if (!user.is_active || user.role === 'suspended') {
      return { status: 'suspended', color: 'bg-red-500' };
    }
    if (user.flag_count >= 3) {
      return { status: 'flagged', color: 'bg-orange-500' };
    }
    return { status: 'active', color: 'bg-green-500' };
  };

  return (
    <div className="max-w-5xl mx-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-light text-primary">User Management</h2>
        <p className="text-secondary text-sm">Manage accounts and roles.</p>
      </header>

      {/* Search */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-divider/50 mb-6">
        <div className="relative flex space-x-2">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary" size={18} />
            <input 
              type="text" 
              placeholder="Search by nickname or UUID..." 
              value={searchTerm} 
              onChange={e => setSearchTerm(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSearch()}
              className="w-full bg-background border border-divider/50 rounded-xl pl-12 pr-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" 
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-6 py-3 bg-sage text-white rounded-xl text-sm font-medium hover:bg-sage/90 transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="bg-white rounded-2xl shadow-sm border border-divider/50 p-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto mb-4"></div>
          <p className="text-secondary text-sm">Loading users...</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-divider/50 overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-background border-b border-divider/50">
              <tr>
                <th className="px-6 py-4 font-medium text-secondary">User</th>
                <th className="px-6 py-4 font-medium text-secondary">Role</th>
                <th className="px-6 py-4 font-medium text-secondary">Status</th>
                <th className="px-6 py-4 font-medium text-secondary">Joined</th>
                <th className="px-6 py-4 font-medium text-secondary text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-divider/50">
              {users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-secondary">
                    No users found
                  </td>
                </tr>
              ) : (
                users.map(user => {
                  const userStatus = getStatusFromUser(user);
                  return (
                    <tr key={user.id} className="hover:bg-background/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-primary">
                          {user.username}
                        </div>
                        <div className="text-xs text-secondary font-mono">
                          {user.id.substring(0, 8)}...
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                          user.is_admin ? 'bg-purple-100 text-purple-700' :
                          user.is_moderator ? 'bg-blue-100 text-blue-700' : 
                          user.role === 'suspended' ? 'bg-red-100 text-red-700' : 
                          'bg-secondary/10 text-secondary'
                        }`}>
                          {user.is_admin ? 'admin' : user.is_moderator ? 'moderator' : user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${userStatus.color}`} />
                          <span className="capitalize text-primary">
                            {userStatus.status}
                          </span>
                        </div>
                        {user.flag_count > 0 && (
                          <span className="text-xs text-red-500 mt-0.5 block">
                            {user.flag_count} flags
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-secondary">{formatDate(user.created_at)}</td>
                      <td className="px-6 py-4 text-right">
                        {actionLoading === user.id ? (
                          <div className="flex items-center justify-end">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-sage"></div>
                          </div>
                        ) : (
                          <div className="flex items-center justify-end space-x-2">
                            <button 
                              className="p-2 text-secondary hover:text-primary hover:bg-background rounded-lg transition-colors" 
                              title="View Details"
                              onClick={() => alert(`User details for ${user.username}\nID: ${user.id}\nEmail: ${user.email || 'N/A'}\nRisk Level: ${user.risk_level}`)}
                            >
                              <Eye size={16} />
                            </button>
                            <button 
                              className="p-2 text-secondary hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" 
                              title="Change Role"
                              onClick={() => {
                                const newRole = prompt('Enter new role (user/moderator):', user.role);
                                if (newRole) handleChangeRole(user.id, newRole);
                              }}
                              disabled={user.is_admin}
                            >
                              <Shield size={16} />
                            </button>
                            <button 
                              className="p-2 text-secondary hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" 
                              title="Suspend User"
                              onClick={() => handleSuspendUser(user.id)}
                              disabled={user.is_admin || user.role === 'suspended'}
                            >
                              <Ban size={16} />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}