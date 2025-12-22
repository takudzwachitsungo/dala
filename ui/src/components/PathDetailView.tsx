import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, CheckCircle2, Circle, PlayCircle, BookOpen, PenLine, Lock } from 'lucide-react';
import { Path, PathStep } from '../api/client';

interface PathDetailViewProps {
  path: Path;
  onBack: () => void;
  onEnroll: () => void;
  onRefresh: () => void;
}

const pathIcons: Record<string, string> = {
  anxiety: '🌊',
  grief: '🕯️',
  burnout: '🌱',
  depression: '💙',
  relationships: '🤝',
  growth: '🌟',
};

const pathColors: Record<string, string> = {
  anxiety: 'bg-orange-50',
  grief: 'bg-blue-50',
  burnout: 'bg-green-50',
  depression: 'bg-indigo-50',
  relationships: 'bg-pink-50',
  growth: 'bg-purple-50',
};

export function PathDetailView({
  path,
  onBack,
  onEnroll,
  onRefresh
}: PathDetailViewProps) {
  const isEnrolled = path.user_progress !== undefined;
  const progress = path.user_progress?.progress_percentage || 0;
  const steps = path.steps || [];
  const currentStepIndex = path.user_progress?.current_step_index || 0;

  const getIcon = (type: string) => {
    switch (type) {
      case 'exercise':
        return <PlayCircle size={16} />;
      case 'journal':
        return <PenLine size={16} />;
      case 'reading':
        return <BookOpen size={16} />;
      default:
        return <Circle size={16} />;
    }
  };

  const handleStepClick = (step: PathStep) => {
    // TODO: Navigate to step content or mark as complete
    console.log('Step clicked:', step);
  };

  const handleEnrollClick = () => {
    onEnroll();
  };

  return <motion.div initial={{
    opacity: 0,
    x: 20
  }} animate={{
    opacity: 1,
    x: 0
  }} exit={{
    opacity: 0,
    x: 20
  }} className="pb-24 px-6 pt-8 max-w-2xl mx-auto min-h-screen bg-background">
      {/* Header */}
      <button onClick={onBack} className="mb-6 p-2 -ml-2 text-secondary hover:text-primary transition-colors rounded-full hover:bg-secondary/10 inline-flex">
        <ArrowLeft size={20} />
      </button>

      <div className={`rounded-3xl p-8 mb-8 ${pathColors[path.category] || 'bg-gray-50'}`}>
        <div className="flex items-center justify-between mb-6">
          <div className={`w-14 h-14 rounded-2xl bg-white/80 flex items-center justify-center text-3xl shadow-sm`}>
            {pathIcons[path.category] || '📚'}
          </div>
          <div className="text-right">
            <span className="text-2xl font-light text-primary">
              {Math.round(progress)}%
            </span>
            <p className="text-[10px] text-secondary uppercase tracking-wider">
              Complete
            </p>
          </div>
        </div>

        <h1 className="text-2xl font-medium text-primary mb-2">{path.name}</h1>
        <p className="text-sm text-primary/70 leading-relaxed mb-6">
          {path.category.charAt(0).toUpperCase() + path.category.slice(1)} • {path.difficulty} • {path.step_count} steps
          {path.estimated_duration && ` • ${path.estimated_duration} days`}
        </p>

        {/* Progress Bar */}
        {isEnrolled ? (
          <div className="w-full bg-white/50 h-2 rounded-full overflow-hidden">
            <motion.div initial={{
            width: 0
          }} animate={{
            width: `${progress}%`
          }} transition={{
            duration: 1,
            ease: 'easeOut'
          }} className="h-full bg-sage rounded-full" />
          </div>
        ) : (
          <button
            onClick={handleEnrollClick}
            className="w-full py-3 rounded-xl text-sm font-medium bg-sage text-white hover:bg-sage-hover transition-colors"
          >
            Start This Journey
          </button>
        )}
      </div>

      {/* Steps List */}
      <div className="space-y-4">
        <h2 className="text-sm font-medium text-secondary uppercase tracking-widest mb-4">
          Your Journey
        </h2>

        {steps.length === 0 && (
          <div className="text-center py-8 text-secondary text-sm">
            {isEnrolled ? 'No steps available yet.' : 'Enroll to see the journey steps!'}
          </div>
        )}

        {steps.map((step, index) => {
          const isCompleted = isEnrolled && index < currentStepIndex;
          const isCurrent = isEnrolled && index === currentStepIndex;
          const isLocked = isEnrolled && index > currentStepIndex;

          return (
            <motion.button 
              key={step.id} 
              onClick={() => !isLocked && handleStepClick(step)} 
              disabled={isLocked} 
              initial={{
                opacity: 0,
                y: 10
              }} 
              animate={{
                opacity: 1,
                y: 0
              }} 
              transition={{
                delay: index * 0.1
              }} 
              className={`w-full text-left group relative bg-white rounded-2xl p-5 shadow-sm border transition-all flex items-start space-x-4 ${isLocked ? 'opacity-60 border-divider/30 cursor-not-allowed' : 'border-divider/50 hover:border-sage/50 hover:shadow-md'}`}
            >
              <div className={`mt-1 transition-colors ${isCompleted ? 'text-sage' : isLocked ? 'text-secondary/50' : 'text-secondary'}`}>
                {isCompleted ? <CheckCircle2 size={20} className="fill-sage/10" /> : isLocked ? <Lock size={20} /> : <div className="w-5 h-5 rounded-full border-2 border-current" />}
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className={`text-sm font-medium ${isLocked ? 'text-secondary' : 'text-primary'}`}>
                    {step.title}
                  </h3>
                  <span className="text-[10px] text-secondary bg-secondary/5 px-2 py-0.5 rounded-full">
                    {step.estimated_minutes || 5} min
                  </span>
                </div>
                <p className="text-xs text-secondary leading-relaxed pr-4">
                  {step.content.substring(0, 120)}...
                </p>

                <div className="mt-3 flex items-center space-x-2 text-[10px] font-medium text-secondary uppercase tracking-wide">
                  {getIcon(step.step_type)}
                  <span>{step.step_type}</span>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </motion.div>;
}