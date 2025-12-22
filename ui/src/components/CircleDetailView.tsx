import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Users, ShieldCheck } from 'lucide-react';
import { PostCard } from './PostCard';
import { PostComposer } from './PostComposer';
import { apiClient, Circle, Post } from '../api/client';

interface CircleDetailViewProps {
  circle: Circle;
  posts: Post[];
  onBack: () => void;
  onJoin: () => void;
  onLeave: () => void;
  onReact: (postId: number) => void;
  onRefresh: () => void;
}

export function CircleDetailView({
  circle,
  posts,
  onBack,
  onJoin,
  onLeave,
  onReact,
  onRefresh,
}: CircleDetailViewProps) {
  const [posting, setPosting] = useState(false);
  const [isAnonymous, setIsAnonymous] = useState(false);

  const handleNewPost = async (content: string) => {
    try {
      setPosting(true);
      await apiClient.createPost(circle.id, content, isAnonymous);
      onRefresh();
    } catch (error) {
      console.error('Failed to create post:', error);
    } finally {
      setPosting(false);
    }
  };

  const handleReply = async (postId: number, content: string, isAnon: boolean) => {
    try {
      await apiClient.replyToPost(postId, content, isAnon);
      onRefresh();
    } catch (error) {
      console.error('Failed to reply:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="pb-24 px-6 pt-8 max-w-2xl mx-auto min-h-screen bg-background"
    >
      {/* Header */}
      <div className="flex items-center mb-6">
        <button
          onClick={onBack}
          className="p-2 -ml-2 text-secondary hover:text-primary transition-colors rounded-full hover:bg-secondary/10"
        >
          <ArrowLeft size={20} />
        </button>
        <div className="ml-2 flex-1">
          <h1 className="text-xl font-medium text-primary">{circle.name}</h1>
          <div className="flex items-center text-xs text-secondary">
            <Users size={12} className="mr-1" />
            <span>{circle.member_count} members</span>
          </div>
        </div>
        {circle.is_member ? (
          <button
            onClick={onLeave}
            className="px-4 py-1.5 rounded-full text-xs font-medium transition-all bg-sage/10 text-sage border border-sage/20 hover:bg-sage/20"
          >
            Joined
          </button>
        ) : (
          <button
            onClick={onJoin}
            className="px-4 py-1.5 rounded-full text-xs font-medium transition-all bg-primary text-white hover:bg-primary/90"
          >
            Join Circle
          </button>
        )}
      </div>

      {/* Description */}
      {circle.description && (
        <div className="mb-6 text-sm text-secondary">
          {circle.description}
        </div>
      )}

      {/* Guidelines Banner */}
      <div className="bg-blue-50/50 border border-blue-100 rounded-xl p-4 mb-6 flex items-start space-x-3">
        <ShieldCheck className="text-blue-400 shrink-0 mt-0.5" size={16} />
        <div>
          <h3 className="text-xs font-medium text-blue-900 mb-1">
            Safe Space Guidelines
          </h3>
          <p className="text-[11px] text-blue-800/70 leading-relaxed">
            This is a judgment-free zone. Please be kind, respectful, and
            supportive. We're all here to heal together.
          </p>
        </div>
      </div>

      {/* Composer - Only show if member */}
      {circle.is_member && (
        <div className="mb-8">
          <PostComposer
            onSubmit={handleNewPost}
            placeholder={`Share with the ${circle.name} circle...`}
            disabled={posting}
          />
          <div className="mt-2 flex items-center justify-end">
            <label className="flex items-center text-xs text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
                className="mr-2 rounded"
              />
              Post anonymously
            </label>
          </div>
        </div>
      )}

      {/* Feed */}
      <div className="space-y-4">
        {posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-secondary text-sm">
              {circle.is_member
                ? 'No posts yet. Be the first to share!'
                : 'Join this circle to see posts and share.'}
            </p>
          </div>
        ) : (
          posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onReact={() => onReact(post.id)}
              onReply={handleReply}
            />
          ))
        )}
      </div>
    </motion.div>
  );
}