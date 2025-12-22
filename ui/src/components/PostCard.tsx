import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Heart, MessageSquare, MoreHorizontal, Flag, Hash } from 'lucide-react';
import { Post as PostType } from '../api/client';

interface PostCardProps {
  post: PostType;
  onReact: (id: number) => void;
  onReply?: (postId: number, content: string, isAnonymous: boolean) => void;
  showCircleBadge?: boolean;
}

export function PostCard({ post, onReact, onReply, showCircleBadge = false }: PostCardProps) {
  const [isRelating, setIsRelating] = useState(post.user_reaction !== undefined);
  const [relatesCount, setRelatesCount] = useState(post.reaction_count);
  const [showReplyBox, setShowReplyBox] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [replyAnonymous, setReplyAnonymous] = useState(false);
  const [replyingToId, setReplyingToId] = useState<number | null>(null); // Track which reply we're responding to

  const handleRelate = () => {
    setIsRelating(!isRelating);
    setRelatesCount((prev) => (isRelating ? prev - 1 : prev + 1));
    onReact(post.id);
  };

  const handleSubmitReply = () => {
    if (replyContent.trim() && onReply) {
      // If replyingToId is set, we're replying to a reply, otherwise to the main post
      const targetId = replyingToId || post.id;
      onReply(targetId, replyContent, replyAnonymous);
      setReplyContent('');
      setShowReplyBox(false);
      setReplyAnonymous(false);
      setReplyingToId(null);
    }
  };

  const handleReplyToReply = (replyId: number) => {
    setReplyingToId(replyId);
    setShowReplyBox(true);
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-divider/50 hover:border-sage/30 transition-colors"
    >
      {/* Circle Badge */}
      {showCircleBadge && post.circle_name && (
        <div className="mb-3 inline-flex items-center space-x-1 bg-sage/10 text-sage px-2 py-1 rounded-full text-[10px] font-medium">
          <Hash size={10} />
          <span>{post.circle_name}</span>
        </div>
      )}
      
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-full bg-sage/20 flex items-center justify-center text-[10px] font-bold text-sage">
            {post.author_name?.[0] || 'A'}
          </div>
          <span className="text-xs font-medium text-primary">
            {post.author_name || 'Anonymous'}
          </span>
          <span className="text-[10px] text-secondary">
            • {formatTime(post.created_at)}
          </span>
        </div>
        <button className="text-secondary hover:text-primary transition-colors">
          <MoreHorizontal size={16} />
        </button>
      </div>

      <p className="text-sm text-primary leading-relaxed mb-4 whitespace-pre-wrap">
        {post.content}
      </p>

      <div className="flex items-center space-x-6">
        <button
          onClick={handleRelate}
          className={`flex items-center space-x-1.5 transition-colors group ${
            isRelating ? 'text-sage' : 'text-secondary hover:text-sage'
          }`}
        >
          <motion.div
            whileTap={{ scale: 0.8 }}
            animate={{ scale: isRelating ? [1, 1.2, 1] : 1 }}
          >
            <Heart
              size={16}
              className={isRelating ? 'fill-sage' : 'group-hover:fill-sage/20'}
            />
          </motion.div>
          <span className="text-xs font-medium">
            {relatesCount > 0 ? `${relatesCount} relate` : 'Relate'}
          </span>
        </button>

        {onReply && (
          <button
            onClick={() => setShowReplyBox(!showReplyBox)}
            className="flex items-center space-x-1.5 text-secondary hover:text-primary transition-colors"
          >
            <MessageSquare size={16} />
            <span className="text-xs font-medium">
              {post.reply_count > 0 ? `${post.reply_count} replies` : 'Reply'}
            </span>
          </button>
        )}
      </div>

      {/* Reply Box */}
      {showReplyBox && onReply && (
        <div className="mt-4 pt-4 border-t border-divider/30">
          {replyingToId && (
            <div className="mb-2 text-[10px] text-secondary flex items-center justify-between">
              <span>Replying to a comment</span>
              <button
                onClick={() => {
                  setReplyingToId(null);
                  setShowReplyBox(false);
                }}
                className="text-sage hover:text-sage/80"
              >
                Cancel
              </button>
            </div>
          )}
          <textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder="Share your thoughts..."
            className="w-full border border-divider/50 rounded-xl p-3 text-sm resize-none focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage"
            rows={3}
          />
          <div className="flex items-center justify-between mt-2">
            <label className="flex items-center text-xs text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={replyAnonymous}
                onChange={(e) => setReplyAnonymous(e.target.checked)}
                className="mr-2 rounded"
              />
              Reply anonymously
            </label>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowReplyBox(false)}
                className="px-3 py-1.5 text-xs text-secondary hover:text-primary"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitReply}
                disabled={!replyContent.trim()}
                className="px-3 py-1.5 bg-sage text-white text-xs rounded-lg hover:bg-sage/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reply
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Replies */}
      {post.replies && post.replies.length > 0 && (
        <div className="mt-4 pt-4 border-t border-divider/30 space-y-3">
          {post.replies.map((reply) => (
            <div key={reply.id} className="pl-4 border-l-2 border-divider/30">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 rounded-full bg-sage/10 flex items-center justify-center text-[9px] font-bold text-sage">
                    {reply.author_name?.[0] || 'A'}
                  </div>
                  <span className="text-xs font-medium text-primary">
                    {reply.author_name || 'Anonymous'}
                  </span>
                  <span className="text-[10px] text-secondary">
                    • {formatTime(reply.created_at)}
                  </span>
                </div>
                {onReply && (
                  <button
                    onClick={() => handleReplyToReply(reply.id)}
                    className="text-[10px] text-sage hover:text-sage/80 font-medium"
                  >
                    Reply
                  </button>
                )}
              </div>
              <p className="text-sm text-primary leading-relaxed mb-2">
                {reply.content}
              </p>
              
              {/* Nested replies to this reply */}
              {reply.replies && reply.replies.length > 0 && (
                <div className="mt-2 space-y-2 pl-4 border-l border-divider/20">
                  {reply.replies.map((nestedReply) => (
                    <div key={nestedReply.id}>
                      <div className="flex items-center space-x-2 mb-1">
                        <div className="w-4 h-4 rounded-full bg-sage/10 flex items-center justify-center text-[8px] font-bold text-sage">
                          {nestedReply.author_name?.[0] || 'A'}
                        </div>
                        <span className="text-[11px] font-medium text-primary">
                          {nestedReply.author_name || 'Anonymous'}
                        </span>
                        <span className="text-[9px] text-secondary">
                          • {formatTime(nestedReply.created_at)}
                        </span>
                      </div>
                      <p className="text-xs text-primary leading-relaxed">
                        {nestedReply.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}