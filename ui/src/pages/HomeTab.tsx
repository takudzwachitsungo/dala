import React, { useState, useEffect, useRef } from 'react';
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
  // Get time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    if (hour < 21) return 'Good evening';
    return 'Good night';
  };

  // Capitalize first letter of name
  const capitalizedName = username ? username.charAt(0).toUpperCase() + username.slice(1) : '';
  const [selectedMood, setSelectedMood] = useState<number>(3);
  const [entries, setEntries] = useState<Entry[]>([]);
  const [moodLogged, setMoodLogged] = useState(false);
  const [dailyVerse, setDailyVerse] = useState<any>(null);
  const [showVerse, setShowVerse] = useState(false);
  const [isLoadingEntries, setIsLoadingEntries] = useState(true);
  const journalFormRef = useRef<{ focus: () => void }>(null);

  // Load journal entries on mount
  useEffect(() => {
    const loadEntries = async () => {
      try {
        setIsLoadingEntries(true);
        const history = await apiClient.getMoodHistory(30); // Get last 30 days
        
        // Convert mood entries to Entry format, only include those with notes
        const loadedEntries: Entry[] = history.entries
          .filter((entry: any) => entry.notes && entry.notes.trim())
          .map((entry: any) => ({
            id: entry.id,
            text: entry.notes,
            mood: entry.mood_score,
            timestamp: new Date(entry.created_at)
          }));
        
        setEntries(loadedEntries);
      } catch (error) {
        console.error('Failed to load journal entries:', error);
      } finally {
        setIsLoadingEntries(false);
      }
    };
    
    loadEntries();
  }, []);

  const handleMoodSelect = async (mood: number) => {
    setSelectedMood(mood);
    
    // Log mood to backend
    try {
      await apiClient.logMood(mood, []);
      setMoodLogged(true);
      console.log('Mood logged successfully:', mood);
      
      // Fetch daily verse based on mood
      const moodNames = ['sad', 'sad', 'anxious', 'default', 'happy', 'grateful'];
      const moodName = moodNames[mood - 1] || 'default';
      
      const verse = await apiClient.getDailyVerse(moodName);
      setDailyVerse(verse);
      
      // Show verse after a brief delay for smooth transition
      setTimeout(() => setShowVerse(true), 500);
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
          {getGreeting()}{capitalizedName && !username?.toLowerCase().includes('anonymous') && `, ${capitalizedName}`}
        </h1>
        <p className="text-secondary text-sm tracking-wide">
          Take a moment to arrive.
        </p>
      </motion.header>

      {/* Mood Check-in / Daily Verse */}
      <motion.section variants={itemVariants} className="mb-12 bg-white/50 rounded-3xl p-6 shadow-sm border border-white">
        {!showVerse ? (
          // Mood selector - shows before logging
          <>
            <motion.h2 
              className="text-center text-sm font-medium text-secondary mb-6 uppercase tracking-widest"
              exit={{ opacity: 0, y: -10 }}
            >
              How are you feeling?
            </motion.h2>
            <motion.div exit={{ opacity: 0, scale: 0.95 }}>
              <MoodSelector selectedMood={selectedMood} onSelectMood={handleMoodSelect} />
            </motion.div>
            {moodLogged && (
              <motion.p 
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center text-xs text-sage mt-4"
              >
                ✓ Mood logged
              </motion.p>
            )}
          </>
        ) : (
          // Daily Verse - replaces mood selector after logging
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="text-center"
          >
            <div className="inline-block bg-gradient-to-r from-sage/20 to-orange/20 rounded-full px-4 py-1 mb-6">
              <span className="text-xs font-medium text-sage uppercase tracking-wider">
                A Word for You
              </span>
            </div>
            
            <motion.blockquote
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-primary font-serif italic text-lg leading-relaxed mb-3 px-2"
            >
              "{dailyVerse?.verse}"
            </motion.blockquote>
            
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-sage text-sm font-medium mb-5"
            >
              — {dailyVerse?.reference}
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-sage/5 rounded-2xl p-4 border border-sage/10"
            >
              <p className="text-secondary text-sm leading-relaxed">
                {dailyVerse?.devotional}
              </p>
            </motion.div>
          </motion.div>
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
        
        {isLoadingEntries ? (
          <div className="flex justify-center items-center py-12 bg-white rounded-2xl border border-divider/30">
            <div className="text-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-sage mx-auto mb-3"></div>
              <p className="text-secondary text-xs">Loading your reflections...</p>
            </div>
          </div>
        ) : (
          <EntryList entries={entries} />
        )}
      </motion.section>
    </motion.div>;
}