import React, { useState } from 'react';
import { Search, MoreHorizontal, Shield, Ban, Eye } from 'lucide-react';
export function UserManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const users = [{
    id: 'u1',
    nickname: 'GentleRain',
    role: 'member',
    joinDate: 'Jan 15, 2024',
    status: 'active',
    flags: 0
  }, {
    id: 'u2',
    nickname: 'QuietSoul',
    role: 'member',
    joinDate: 'Feb 2, 2024',
    status: 'flagged',
    flags: 3
  }, {
    id: 'u3',
    nickname: 'SupportiveFriend',
    role: 'peer_supporter',
    joinDate: 'Dec 10, 2023',
    status: 'active',
    flags: 0
  }, {
    id: 'u4',
    nickname: 'User992',
    role: 'suspended',
    joinDate: 'Mar 1, 2024',
    status: 'suspended',
    flags: 12
  }];
  const filteredUsers = users.filter(u => u.nickname.toLowerCase().includes(searchTerm.toLowerCase()) || u.id.toLowerCase().includes(searchTerm.toLowerCase()));
  return <div className="max-w-5xl mx-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-light text-primary">User Management</h2>
        <p className="text-secondary text-sm">Manage accounts and roles.</p>
      </header>

      {/* Search */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-divider/50 mb-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary" size={18} />
          <input type="text" placeholder="Search by nickname or UUID..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full bg-background border border-divider/50 rounded-xl pl-12 pr-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" />
        </div>
      </div>

      {/* Table */}
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
            {filteredUsers.map(user => <tr key={user.id} className="hover:bg-background/50 transition-colors">
                <td className="px-6 py-4">
                  <div className="font-medium text-primary">
                    {user.nickname}
                  </div>
                  <div className="text-xs text-secondary font-mono">
                    {user.id}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${user.role === 'peer_supporter' ? 'bg-blue-100 text-blue-700' : user.role === 'suspended' ? 'bg-red-100 text-red-700' : 'bg-secondary/10 text-secondary'}`}>
                    {user.role.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${user.status === 'active' ? 'bg-green-500' : user.status === 'flagged' ? 'bg-orange-500' : 'bg-red-500'}`} />
                    <span className="capitalize text-primary">
                      {user.status}
                    </span>
                  </div>
                  {user.flags > 0 && <span className="text-xs text-red-500 mt-0.5 block">
                      {user.flags} flags
                    </span>}
                </td>
                <td className="px-6 py-4 text-secondary">{user.joinDate}</td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button className="p-2 text-secondary hover:text-primary hover:bg-background rounded-lg transition-colors" title="View Details">
                      <Eye size={16} />
                    </button>
                    <button className="p-2 text-secondary hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Change Role">
                      <Shield size={16} />
                    </button>
                    <button className="p-2 text-secondary hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Suspend User">
                      <Ban size={16} />
                    </button>
                  </div>
                </td>
              </tr>)}
          </tbody>
        </table>
      </div>
    </div>;
}