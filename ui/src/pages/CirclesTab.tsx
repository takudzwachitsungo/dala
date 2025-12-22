import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Search, Plus } from 'lucide-react';
import { CircleDetailView } from '../components/CircleDetailView';
import { PostCard } from '../components/PostCard';
import { apiClient, Circle, Post } from '../api/client';

export function CirclesTab() {
  const [selectedCircleId, setSelectedCircleId] = useState<number | null>(null);
  const [circles, setCircles] = useState<Circle[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [feedPosts, setFeedPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingFeed, setLoadingFeed] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadCircles();
  }, []);

  // Load feed posts after circles are loaded
  useEffect(() => {
    if (!loading && circles.length > 0) {
      loadFeedPosts();
    }
  }, [loading, circles]);

  useEffect(() => {
    if (selectedCircleId) {
      const circle = circles.find(c => c.id === selectedCircleId);
      // Only load posts if user is a member
      if (circle?.is_member) {
        loadCirclePosts(selectedCircleId);
      } else {
        setPosts([]);
      }
    }
  }, [selectedCircleId, circles]);

  const loadCircles = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getCircles(0, 20);
      setCircles(data);
    } catch (error) {
      console.error('Failed to load circles:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFeedPosts = async () => {
    try {
      setLoadingFeed(true);
      // Get all joined circles
      const joinedCircles = circles.filter(c => c.is_member);
      
      if (joinedCircles.length === 0) {
        setFeedPosts([]);
        setLoadingFeed(false);
        return;
      }

      // Fetch posts from all joined circles and attach circle names
      const allPosts: Post[] = [];
      for (const circle of joinedCircles) {
        try {
          const circlePosts = await apiClient.getCirclePosts(circle.id, 0, 10);
          // Add circle name to each post
          const postsWithCircle = circlePosts.map(post => ({
            ...post,
            circle_name: circle.name
          }));
          allPosts.push(...postsWithCircle);
        } catch (error) {
          console.error(`Failed to load posts from circle ${circle.id}:`, error);
        }
      }

      // Sort by created_at (most recent first)
      allPosts.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      
      setFeedPosts(allPosts);
    } catch (error) {
      console.error('Failed to load feed posts:', error);
    } finally {
      setLoadingFeed(false);
    }
  };

  const loadCirclePosts = async (circleId: number) => {
    try {
      const data = await apiClient.getCirclePosts(circleId, 0, 20);
      setPosts(data);
    } catch (error) {
      console.error('Failed to load posts:', error);
    }
  };

  const handleJoinCircle = async (circleId: number) => {
    try {
      await apiClient.joinCircle(circleId);
      await loadCircles();
      await loadFeedPosts(); // Refresh feed after joining
      // Reload posts after joining
      if (selectedCircleId === circleId) {
        loadCirclePosts(circleId);
      }
    } catch (error) {
      console.error('Failed to join circle:', error);
    }
  };

  const handleLeaveCircle = async (circleId: number) => {
    try {
      await apiClient.leaveCircle(circleId);
      await loadCircles();
      await loadFeedPosts(); // Refresh feed after leaving
      // Clear posts after leaving
      if (selectedCircleId === circleId) {
        setPosts([]);
      }
    } catch (error) {
      console.error('Failed to leave circle:', error);
    }
  };

  const handleReact = async (postId: number) => {
    try {
      const post = feedPosts.find(p => p.id === postId) || posts.find(p => p.id === postId);
      if (post?.user_reaction) {
        await apiClient.removeReaction(postId);
      } else {
        await apiClient.addReaction(postId, 'relate');
      }
      // Refresh appropriate feed
      if (selectedCircleId) {
        loadCirclePosts(selectedCircleId);
      } else {
        loadFeedPosts();
      }
    } catch (error) {
      console.error('Failed to react to post:', error);
    }
  };

  const handleReplyToFeedPost = async (postId: number, content: string, isAnonymous: boolean) => {
    try {
      await apiClient.replyToPost(postId, content, isAnonymous);
      // Refresh the feed to show the new reply
      await loadFeedPosts();
    } catch (error) {
      console.error('Failed to reply to post:', error);
    }
  };

  const selectedCircle = circles.find(c => c.id === selectedCircleId);

  const filteredCircles = circles.filter(circle =>
    circle.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    circle.topic.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="pb-24 px-6 pt-12 max-w-2xl mx-auto">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
          <p className="text-secondary text-sm mt-4">Loading circles...</p>
        </div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      {selectedCircle ? (
        <CircleDetailView
          key="detail"
          circle={selectedCircle}
          posts={posts}
          onBack={() => setSelectedCircleId(null)}
          onJoin={() => handleJoinCircle(selectedCircle.id)}
          onLeave={() => handleLeaveCircle(selectedCircle.id)}
          onReact={handleReact}
          onRefresh={() => loadCirclePosts(selectedCircle.id)}
        />
      ) : (
        <motion.div
          key="list"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="pb-24 px-6 pt-12 max-w-2xl mx-auto"
        >
          <header className="mb-8">
            <h1 className="text-2xl font-light text-primary mb-2">
              Dala Circles
            </h1>
            <p className="text-secondary text-sm">You are not alone here.</p>
          </header>

          {/* Search */}
          <div className="relative mb-10">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary" size={18} />
            <input
              type="text"
              placeholder="Find a topic or conversation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-divider/50 rounded-2xl pl-12 pr-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all"
            />
          </div>

          {/* Topics Scroll */}
          <div className="flex space-x-3 overflow-x-auto pb-6 -mx-6 px-6 scrollbar-hide mb-8">
            {filteredCircles.map((circle) => (
              <button
                key={circle.id}
                onClick={() => setSelectedCircleId(circle.id)}
                className="flex-shrink-0 bg-white border border-divider/50 rounded-xl px-4 py-3 min-w-[140px] text-left hover:border-sage/50 transition-colors group"
              >
                <h3 className="text-sm font-medium text-primary mb-1 group-hover:text-sage transition-colors">
                  {circle.name}
                </h3>
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-[10px] text-secondary">
                    <Users size={12} className="mr-1" />
                    <span>{circle.member_count}</span>
                  </div>
                  {circle.is_member && (
                    <div className="w-2 h-2 rounded-full bg-sage"></div>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Feed Posts */}
          <div className="space-y-6">
            <h2 className="text-sm font-medium text-secondary uppercase tracking-widest px-2">
              Recent Posts
            </h2>
            
            {loadingFeed ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-sage mx-auto"></div>
                <p className="text-secondary text-xs mt-3">Loading posts...</p>
              </div>
            ) : feedPosts.length > 0 ? (
              feedPosts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  onReact={() => handleReact(post.id)}
                  onReply={handleReplyToFeedPost}
                  showCircleBadge={true}
                />
              ))
            ) : (
              <div className="text-center py-12 bg-white rounded-2xl border border-divider/30">
                <p className="text-secondary text-sm mb-2">No posts yet</p>
                <p className="text-secondary text-xs">Join a circle to see posts from the community</p>
              </div>
            )}
          </div>

          {/* No circles state */}
          {circles.length === 0 && (
            <div className="text-center py-12">
              <p className="text-secondary text-sm">No circles available yet.</p>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}