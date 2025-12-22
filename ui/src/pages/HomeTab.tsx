import React, { useState, Children, useRef } from 'react';
import { motion } from 'framer-motion';
import { MoodSelector } from '../components/MoodSelector';
import { JournalForm } from '../components/JournalForm';
import { EntryList, Entry } from '../components/EntryList';
import { MessageCircle, PenLine, Compass, LogOut } from 'lucide-react';
import { apiClient } from '../api/client';

interface HomeTabProps {
  onNavigate: (tab: 'companion' | 'paths') => void;
  onLogout?: () => void;
  username?: string;
}
export function HomeTab({
  onNavigate,
  onLogout,
  username
}: HomeTabProps) {
  // Capitalize first letter of name
  const capitalizedName = username ? username.charAt(0).toUpperCase() + username.slice(1) : '';
  const [selectedMood, setSelectedMood] = useState<number>(3);
  const [entries, setEntries] = useState<Entry[]>([]);
  const [moodLogged, setMoodLogged] = useState(false);
  const journalFormRef = useRef<{ focus: () => void }>(null);

  const handleMoodSelect = async (mood: number) => {
    setSelectedMood(mood);
    
    // Log mood to backend
    try {
      await apiClient.logMood(mood, []);
      setMoodLogged(true);
      console.log('Mood logged successfully:', mood);
    } catch (error) {
      console.error('Failed to log mood:', error);
    }
  };

  const handleReflectClick = () => {
    journalFormRef.current?.focus();
  };
  const handleAddEntry = async (text: string) => {
    const newEntry: Entry = {
      id: Date.now().toString(),
      text,
      mood: selectedMood,
      timestamp: new Date()
    };
    
    // Add to local state immediately for instant UI feedback
    setEntries([newEntry, ...entries]);
    
    // Save to backend
    try {
      await apiClient.logMood(selectedMood, [], undefined, text);
      console.log('Journal entry saved to backend');
    } catch (error) {
      console.error('Failed to save journal entry:', error);
      // Entry is still in local state even if backend fails
    }
  };
  const containerVariants = {
    hidden: {
      opacity: 0
    },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    },
    exit: {
      opacity: 0
    }
  };
  const itemVariants = {
    hidden: {
      opacity: 0,
      y: 20
    },
    visible: {
      opacity: 1,
      y: 0
    }
  };
  return <motion.div variants={containerVariants} initial="hidden" animate="visible" exit="exit" className="pb-24 px-6 pt-12 max-w-2xl mx-auto">
      {/* Header */}
      <motion.header variants={itemVariants} className="text-center mb-12 relative">
        {onLogout && (
          <button
            onClick={onLogout}
            className="absolute top-0 right-0 flex items-center gap-2 text-secondary hover:text-primary transition-colors text-sm px-3 py-1.5 rounded-lg hover:bg-white/50"
            aria-label="Log out"
          >
            <span className="hidden sm:inline">Log out</span>
            <LogOut size={16} />
          </button>
        )}
        <h1 className="text-3xl font-light text-primary tracking-tight mb-2">
          Good morning{capitalizedName && `, ${capitalizedName}`}
        </h1>
        <p className="text-secondary text-sm tracking-wide">
          Take a moment to arrive.
        </p>
      </motion.header>

      {/* Mood Check-in */}
      <motion.section variants={itemVariants} className="mb-12 bg-white/50 rounded-3xl p-6 shadow-sm border border-white">
        <h2 className="text-center text-sm font-medium text-secondary mb-6 uppercase tracking-widest">
          How are you feeling?
        </h2>
        <MoodSelector selectedMood={selectedMood} onSelectMood={handleMoodSelect} />
        {moodLogged && (
          <motion.p 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center text-xs text-sage mt-4"
          >
            ✓ Mood logged
          </motion.p>
        )}
      </motion.section>

      {/* Quick Actions */}
      <motion.section variants={itemVariants} className="grid grid-cols-3 gap-4 mb-12">
        <button onClick={() => onNavigate('companion')} className="flex flex-col items-center justify-center p-4 bg-white rounded-2xl shadow-sm border border-divider/50 hover:border-sage/50 transition-colors group">
          <div className="w-10 h-10 rounded-full bg-sage/10 flex items-center justify-center text-sage mb-3 group-hover:bg-sage/20 transition-colors">
            <MessageCircle size={20} />
          </div>
          <span className="text-xs font-medium text-primary">Talk to Dala</span>
        </button>

        <button onClick={handleReflectClick} className="flex flex-col items-center justify-center p-4 bg-white rounded-2xl shadow-sm border border-divider/50 hover:border-sage/50 transition-colors group">
          <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 mb-3 group-hover:bg-orange-200 transition-colors">
            <PenLine size={20} />
          </div>
          <span className="text-xs font-medium text-primary">Reflect</span>
        </button>

        <button onClick={() => onNavigate('paths')} className="flex flex-col items-center justify-center p-4 bg-white rounded-2xl shadow-sm border border-divider/50 hover:border-sage/50 transition-colors group">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-3 group-hover:bg-blue-200 transition-colors">
            <Compass size={20} />
          </div>
          <span className="text-xs font-medium text-primary">Explore</span>
        </button>
      </motion.section>

      {/* Journal */}
      <motion.section variants={itemVariants} className="mb-12">
        <JournalForm ref={journalFormRef} onSubmit={handleAddEntry} />
      </motion.section>

      {/* Recent Entries */}
      <motion.section variants={itemVariants}>
        <div className="flex items-center justify-between mb-6 px-2">
          <h3 className="text-sm font-medium text-secondary uppercase tracking-widest">
            Recent Reflections
          </h3>
          <span className="text-xs text-sage font-medium bg-sage/10 px-2 py-1 rounded-full">
            {entries.length} entries
          </span>
        </div>
        <EntryList entries={entries} />
      </motion.section>
    </motion.div>;
}