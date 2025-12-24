import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Eye, BookOpen, X } from 'lucide-react';
import { apiClient } from '../../api/client';

interface Path {
  id: string;
  name: string;
  category: string;
  difficulty: string;
  step_count: number;
  enrollment_count: number;
  estimated_duration?: number;
  is_published: boolean;
  created_at: string;
}

export function PathManagement() {
  const [paths, setPaths] = useState<Path[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    difficulty: 'beginner',
    description: '',
    estimated_duration: '',
    is_published: false
  });

  useEffect(() => {
    loadPaths();
  }, []);

  const loadPaths = async () => {
    try {
      setLoading(true);
      const data = await apiClient.adminGetPaths(0, 100);
      setPaths(data);
    } catch (error) {
      console.error('Failed to load paths:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.adminCreatePath({
        ...formData,
        estimated_duration: formData.estimated_duration ? parseInt(formData.estimated_duration) : undefined
      });
      setShowCreateModal(false);
      setFormData({
        name: '',
        category: '',
        difficulty: 'beginner',
        description: '',
        estimated_duration: '',
        is_published: false
      });
      loadPaths();
    } catch (error) {
      console.error('Failed to create path:', error);
      alert('Failed to create path');
    }
  };

  const handleTogglePublish = async (pathId: string, currentStatus: boolean) => {
    try {
      await apiClient.adminTogglePathPublish(pathId, !currentStatus);
      loadPaths();
    } catch (error) {
      console.error('Failed to toggle publish status:', error);
      alert('Failed to update path');
    }
  };

  const handleDelete = async (pathId: string, pathName: string) => {
    if (!confirm(`Are you sure you want to delete "${pathName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await apiClient.adminDeletePath(pathId);
      loadPaths();
    } catch (error) {
      console.error('Failed to delete path:', error);
      alert('Failed to delete path');
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading paths...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-light text-primary">Path Management</h2>
          <p className="text-secondary text-sm">Create and manage wellness paths</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-sage text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-sage-hover transition-colors flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Create New Path</span>
        </button>
      </header>

      {/* Paths Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {paths.length === 0 ? (
          <div className="col-span-full text-center py-12 bg-white rounded-2xl border border-divider/50">
            <BookOpen size={48} className="mx-auto text-divider mb-4" />
            <p className="text-secondary">No paths created yet</p>
          </div>
        ) : (
          paths.map((path) => (
            <div
              key={path.id}
              className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="font-medium text-primary mb-1">{path.name}</h3>
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="px-2 py-0.5 bg-secondary/10 text-secondary rounded-full capitalize">
                      {path.category}
                    </span>
                    <span className="px-2 py-0.5 bg-secondary/10 text-secondary rounded-full capitalize">
                      {path.difficulty}
                    </span>
                  </div>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    path.is_published
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {path.is_published ? 'Published' : 'Draft'}
                </span>
              </div>

              <div className="space-y-2 mb-4 text-sm text-secondary">
                <div className="flex justify-between">
                  <span>Steps:</span>
                  <span className="font-medium">{path.step_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Enrollments:</span>
                  <span className="font-medium">{path.enrollment_count}</span>
                </div>
                {path.estimated_duration && (
                  <div className="flex justify-between">
                    <span>Duration:</span>
                    <span className="font-medium">{path.estimated_duration} days</span>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2 pt-4 border-t border-divider/50">
                <button
                  onClick={() => handleTogglePublish(path.id, path.is_published)}
                  className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    path.is_published
                      ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      : 'bg-sage text-white hover:bg-sage-hover'
                  }`}
                >
                  {path.is_published ? 'Unpublish' : 'Publish'}
                </button>
                <button
                  onClick={() => handleDelete(path.id, path.name)}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete Path"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-medium text-primary">Create New Path</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-secondary hover:text-primary"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Path Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-divider rounded-xl focus:outline-none focus:ring-2 focus:ring-sage"
                  placeholder="e.g., Managing Anxiety"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Category *
                </label>
                <select
                  required
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-2 border border-divider rounded-xl focus:outline-none focus:ring-2 focus:ring-sage"
                >
                  <option value="">Select category</option>
                  <option value="anxiety">Anxiety</option>
                  <option value="depression">Depression</option>
                  <option value="stress">Stress Management</option>
                  <option value="mindfulness">Mindfulness</option>
                  <option value="self-care">Self-Care</option>
                  <option value="relationships">Relationships</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Difficulty *
                </label>
                <select
                  required
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="w-full px-4 py-2 border border-divider rounded-xl focus:outline-none focus:ring-2 focus:ring-sage"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-divider rounded-xl focus:outline-none focus:ring-2 focus:ring-sage"
                  rows={3}
                  placeholder="Brief description of the path"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Estimated Duration (days)
                </label>
                <input
                  type="number"
                  value={formData.estimated_duration}
                  onChange={(e) => setFormData({ ...formData, estimated_duration: e.target.value })}
                  className="w-full px-4 py-2 border border-divider rounded-xl focus:outline-none focus:ring-2 focus:ring-sage"
                  placeholder="e.g., 7"
                  min="1"
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_published"
                  checked={formData.is_published}
                  onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
                  className="rounded"
                />
                <label htmlFor="is_published" className="text-sm text-secondary">
                  Publish immediately
                </label>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-divider rounded-xl text-sm font-medium text-secondary hover:bg-secondary/5"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-sage text-white rounded-xl text-sm font-medium hover:bg-sage-hover"
                >
                  Create Path
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
