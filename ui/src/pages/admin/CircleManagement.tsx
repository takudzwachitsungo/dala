import React, { useState, useEffect } from 'react';
import { MessageCircle, Users, Edit2, Archive, Plus, X } from 'lucide-react';
import { apiClient } from '../../api/client';

interface Circle {
  id: string;
  name: string;
  topic: string;
  description: string;
  icon: string;
  member_count: number;
  post_count: number;
}

export function CircleManagement() {
  const [circles, setCircles] = useState<Circle[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    topic: '',
    description: '',
    icon: '💬'
  });

  useEffect(() => {
    loadCircles();
  }, []);

  const loadCircles = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getCircles(0, 100);
      setCircles(data);
    } catch (error) {
      console.error('Failed to load circles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.adminCreateCircle(formData);
      setShowCreateModal(false);
      setFormData({ name: '', topic: '', description: '', icon: '💬' });
      loadCircles();
    } catch (error) {
      console.error('Failed to create circle:', error);
      alert('Failed to create circle. Make sure you have moderator permissions.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading circles...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-light text-primary">Circle Management</h2>
          <p className="text-secondary text-sm">
            Manage community topics and guidelines.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-sage text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-sage-hover transition-colors flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Create New Circle</span>
        </button>
      </header>

      <div className="grid gap-4">
        {circles.map((circle) => (
          <div
            key={circle.id}
            className="bg-white rounded-xl p-6 shadow-sm border border-divider/50 flex items-center justify-between"
          >
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-sage/10 text-sage rounded-xl text-2xl">
                {circle.icon || '💬'}
              </div>
              <div>
                <h3 className="font-medium text-primary">{circle.name}</h3>
                <p className="text-xs text-secondary mb-1">{circle.topic}</p>
                <div className="flex items-center space-x-4 text-xs text-secondary">
                  <span className="flex items-center">
                    <Users size={12} className="mr-1" /> {circle.member_count} members
                  </span>
                  <span>{circle.post_count} posts</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button className="p-2 text-secondary hover:text-primary hover:bg-background rounded-lg transition-colors">
                <Edit2 size={18} />
              </button>
              <button className="p-2 text-secondary hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                <Archive size={18} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-medium text-primary">Create New Circle</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 hover:bg-background rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Circle Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl border border-divider focus:border-sage focus:outline-none"
                  placeholder="e.g., Anxiety Support"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Topic
                </label>
                <input
                  type="text"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl border border-divider focus:border-sage focus:outline-none"
                  placeholder="e.g., anxiety, depression"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl border border-divider focus:border-sage focus:outline-none resize-none"
                  rows={3}
                  placeholder="Describe what this circle is for..."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Icon (emoji)
                </label>
                <input
                  type="text"
                  value={formData.icon}
                  onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                  className="w-full px-4 py-2 rounded-xl border border-divider focus:border-sage focus:outline-none"
                  placeholder="💬"
                  maxLength={2}
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 rounded-xl border border-divider text-secondary hover:bg-background transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 rounded-xl bg-sage text-white hover:bg-sage-hover transition-colors"
                >
                  Create Circle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}