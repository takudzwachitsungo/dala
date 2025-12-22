import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Lock, ChevronRight } from 'lucide-react';
import { PathDetailView } from '../components/PathDetailView';
import { apiClient, Path } from '../api/client';

const pathIcons: Record<string, string> = {
  anxiety: '🌊',
  grief: '🕯️',
  burnout: '🌱',
  depression: '💙',
  relationships: '🤝',
  growth: '🌟',
};

const pathColors: Record<string, string> = {
  anxiety: 'bg-orange-100 text-orange-700',
  grief: 'bg-blue-100 text-blue-700',
  burnout: 'bg-green-100 text-green-700',
  depression: 'bg-indigo-100 text-indigo-700',
  relationships: 'bg-pink-100 text-pink-700',
  growth: 'bg-purple-100 text-purple-700',
};

export function PathsTab() {
  const [selectedPathId, setSelectedPathId] = useState<number | null>(null);
  const [paths, setPaths] = useState<Path[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState<string | undefined>(undefined);

  useEffect(() => {
    loadPaths();
  }, [filterCategory]);

  const loadPaths = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getPaths(filterCategory, undefined, 0, 20);
      setPaths(data);
    } catch (error) {
      console.error('Failed to load paths:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (pathId: number) => {
    try {
      await apiClient.enrollInPath(pathId);
      loadPaths();
    } catch (error) {
      console.error('Failed to enroll in path:', error);
    }
  };

  const selectedPath = paths.find((p) => p.id === selectedPathId);

  if (loading) {
    return (
      <div className="pb-24 px-6 pt-12 max-w-2xl mx-auto">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage mx-auto"></div>
          <p className="text-secondary text-sm mt-4">Loading paths...</p>
        </div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      {selectedPath ? (
        <PathDetailView
          key="detail"
          path={selectedPath}
          onBack={() => setSelectedPathId(null)}
          onEnroll={() => handleEnroll(selectedPath.id)}
          onRefresh={loadPaths}
        />
      ) : (
        <motion.div
          key="list"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="pb-24 px-6 pt-12 max-w-2xl mx-auto"
        >
          <header className="mb-10">
            <h1 className="text-2xl font-light text-primary mb-2">
              Your Paths
            </h1>
            <p className="text-secondary text-sm">
              Structured journeys for your wellbeing.
            </p>
          </header>

          {/* Category Filter */}
          <div className="flex space-x-2 overflow-x-auto pb-6 scrollbar-hide mb-6">
            <button
              onClick={() => setFilterCategory(undefined)}
              className={`px-4 py-2 rounded-full text-xs font-medium transition-colors whitespace-nowrap ${
                !filterCategory
                  ? 'bg-sage text-white'
                  : 'bg-secondary/10 text-secondary hover:bg-secondary/20'
              }`}
            >
              All Paths
            </button>
            {['anxiety', 'grief', 'burnout', 'depression', 'relationships', 'growth'].map(
              (cat) => (
                <button
                  key={cat}
                  onClick={() => setFilterCategory(cat)}
                  className={`px-4 py-2 rounded-full text-xs font-medium transition-colors whitespace-nowrap ${
                    filterCategory === cat
                      ? 'bg-sage text-white'
                      : 'bg-secondary/10 text-secondary hover:bg-secondary/20'
                  }`}
                >
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              )
            )}
          </div>

          <div className="grid gap-6">
            {paths.map((path, index) => {
              const progress = path.user_progress?.progress_percentage || 0;
              const isEnrolled = path.user_progress !== undefined;

              return (
                <motion.div
                  key={path.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="group relative bg-white rounded-3xl p-6 shadow-sm border border-divider/50 hover:border-sage/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`w-12 h-12 rounded-2xl ${
                        pathColors[path.category] || 'bg-gray-100 text-gray-700'
                      } flex items-center justify-center text-2xl`}
                    >
                      {pathIcons[path.category] || '📚'}
                    </div>
                    <div className="flex items-center space-x-1 text-xs font-medium text-secondary">
                      <span>{Math.round(progress)}%</span>
                    </div>
                  </div>

                  <h3 className="text-lg font-medium text-primary mb-1">
                    {path.name}
                  </h3>
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="text-xs text-secondary">
                      {path.step_count} steps
                    </span>
                    <span className="text-xs text-secondary">•</span>
                    <span className="text-xs text-secondary capitalize">
                      {path.difficulty}
                    </span>
                    {path.estimated_duration && (
                      <>
                        <span className="text-xs text-secondary">•</span>
                        <span className="text-xs text-secondary">
                          {path.estimated_duration} days
                        </span>
                      </>
                    )}
                  </div>

                  {/* Progress Bar */}
                  {isEnrolled && (
                    <div className="w-full bg-secondary/10 h-1.5 rounded-full overflow-hidden mb-6">
                      <div
                        className="h-full bg-sage rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  )}

                  <button
                    onClick={() => setSelectedPathId(path.id)}
                    className="w-full py-3 rounded-xl text-sm font-medium flex items-center justify-center space-x-2 transition-colors bg-primary text-white hover:bg-primary/90"
                  >
                    {isEnrolled ? (
                      <>
                        <span>Continue</span>
                        <ChevronRight size={16} />
                      </>
                    ) : (
                      <>
                        <Play size={16} />
                        <span>Start Journey</span>
                      </>
                    )}
                  </button>
                </motion.div>
              );
            })}
          </div>

          {paths.length === 0 && (
            <div className="text-center py-12">
              <p className="text-secondary text-sm">
                No paths available in this category.
              </p>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}