import React, { useState, useEffect } from 'react';
import { Filter, Check } from 'lucide-react';
import { FlaggedContentCard } from '../../components/admin/FlaggedContentCard';
import { apiClient } from '../../api/client';

interface FlaggedPost {
  id: string;
  content: string;
  author_name: string;
  flag_reason: string;
  flag_severity: string;
  created_at: string;
}

export function ContentModeration() {
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'medium' | 'low'>('all');
  const [queue, setQueue] = useState<FlaggedPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFlaggedPosts();
  }, [filter]);

  const loadFlaggedPosts = async () => {
    try {
      setLoading(true);
      const severity = filter === 'all' ? undefined : filter;
      const posts = await apiClient.adminGetFlaggedPosts(severity, 0, 50);
      setQueue(posts.map((post: any) => ({
        id: post.id,
        content: post.content,
        author_name: post.author_name || 'Anonymous',
        flag_reason: post.flag_reason || 'Flagged by community',
        flag_severity: post.flag_severity || 'medium',
        created_at: new Date(post.created_at).toLocaleString()
      })));
    } catch (error) {
      console.error('Failed to load flagged posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id: string, action: string) => {
    try {
      if (action === 'hide') {
        await apiClient.hidePost(id);
      } else if (action === 'unhide') {
        await apiClient.unhidePost(id);
      }
      setQueue(queue.filter(item => item.id !== id));
    } catch (error) {
      console.error(`Failed to ${action} post:`, error);
      alert(`Failed to ${action} post. Make sure you have moderator permissions.`);
    }
  };

  const filteredQueue = queue;

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
        <p className="text-secondary text-sm mt-4">Loading flagged content...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-light text-primary">Content Moderation</h2>
          <p className="text-secondary text-sm">Review and action flagged content.</p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-secondary mr-2">Filter by risk:</span>
          {(['all', 'critical', 'high', 'medium', 'low'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium capitalize transition-colors ${
                filter === f
                  ? 'bg-primary text-white'
                  : 'bg-white border border-divider text-secondary hover:border-primary'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </header>

      {filteredQueue.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-secondary">No flagged content found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredQueue.map((item) => (
            <FlaggedContentCard
              key={item.id}
              {...item}
              timestamp={item.created_at}
              severity={item.flag_severity as 'low' | 'medium' | 'high' | 'critical'}
              reason={item.flag_reason}
              author={item.author_name}
              onApprove={() => handleAction(item.id, 'unhide')}
              onHide={() => handleAction(item.id, 'hide')}
              onEscalate={() => console.log('Escalate:', item.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}