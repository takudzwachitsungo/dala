import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Settings, Award, Calendar, ShieldAlert, LogOut } from 'lucide-react';
import { apiClient } from '../api/client';
import { SafetyPlanModal } from '../components/SafetyPlanModal';

interface ProfileTabProps {
  onLogout?: () => void;
  isActive?: boolean;
}

interface ProfileData {
  username: string;
  created_at: string;
  streak_days: number;
  total_mood_entries: number;
  total_conversations: number;
  milestone_count: number;
  is_admin: boolean;
  is_anonymous: boolean;
  role: string;
}

interface MoodHistoryEntry {
  mood_score: number;
  created_at: string;
}

export function ProfileTab({ onLogout, isActive }: ProfileTabProps) {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [moodHistory, setMoodHistory] = useState<MoodHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSafetyPlan, setShowSafetyPlan] = useState(false);

  useEffect(() => {
    loadProfile();
    loadMoodHistory();
  }, []);

  // Reload mood history when tab becomes active
  useEffect(() => {
    if (isActive) {
      loadMoodHistory();
    }
  }, [isActive]);

  const loadProfile = async () => {
    try {
      const data = await apiClient.getProfile();
      console.log('Profile data received:', data);
      console.log('Username from data:', data.username);
      console.log('Full data keys:', Object.keys(data));
      console.log('is_admin value:', data.is_admin);
      console.log('role value:', data.role);
      setProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMoodHistory = async () => {
    try {
      const data = await apiClient.getMoodHistory(7); // Last 7 days
      setMoodHistory(data.entries || []);
    } catch (error) {
      console.error('Failed to load mood history:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage"></div>
      </div>
    );
  }

  const username = profile?.username || 'User';
  const firstLetter = username.charAt(0).toUpperCase();
  const memberSince = profile?.created_at ? formatDate(profile.created_at) : 'Recently';

  return <div className="pb-24 px-6 pt-12 max-w-2xl mx-auto">
      <header className="flex items-center justify-between mb-10">
        <h1 className="text-2xl font-light text-primary">Your Space</h1>
        <div className="flex items-center space-x-2">
          <button className="p-2 text-secondary hover:text-primary transition-colors">
            <Settings size={20} />
          </button>
          {onLogout && (
            <button 
              onClick={onLogout}
              className="p-2 text-secondary hover:text-red-500 transition-colors"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          )}
        </div>
      </header>

      {/* Profile Card */}
      <div className="bg-white rounded-3xl p-6 shadow-sm border border-divider/50 mb-8 flex items-center space-x-4">
        <div className="w-16 h-16 rounded-full bg-sage/20 flex items-center justify-center text-2xl text-sage">
          {firstLetter}
        </div>
        <div>
          <h2 className="text-lg font-medium text-primary">{username}</h2>
          <p className="text-sm text-secondary">Member since {memberSince}</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-divider/50">
          <div className="flex items-center space-x-2 text-sage mb-2">
            <Calendar size={18} />
            <span className="text-xs font-medium uppercase tracking-wide">
              Streak
            </span>
          </div>
          <p className="text-2xl font-light text-primary">{profile?.streak_days || 0} Days</p>
          <p className="text-xs text-secondary mt-1">
            Keep showing up for yourself.
          </p>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-divider/50">
          <div className="flex items-center space-x-2 text-orange-400 mb-2">
            <Award size={18} />
            <span className="text-xs font-medium uppercase tracking-wide">
              Milestones
            </span>
          </div>
          <p className="text-2xl font-light text-primary">{profile?.milestone_count || 0}</p>
          <p className="text-xs text-secondary mt-1">
            {profile?.total_conversations || 0} conversations • {profile?.total_mood_entries || 0} mood logs
          </p>
        </div>
      </div>

      {/* Safety Plan */}
      <div className="bg-red-50/50 rounded-2xl p-6 border border-red-100 mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-500">
            <ShieldAlert size={16} />
          </div>
          <h3 className="text-sm font-medium text-red-900">My Safety Plan</h3>
        </div>
        <p className="text-sm text-red-800/70 mb-4 leading-relaxed">
          A private space for your coping strategies and emergency contacts.
          Only you can see this.
        </p>
        <button 
          onClick={() => setShowSafetyPlan(true)}
          className="text-xs font-medium text-red-600 bg-white border border-red-200 px-4 py-2 rounded-lg hover:bg-red-50 transition-colors"
        >
          View Plan
        </button>
      </div>

      {/* Mood History */}
      <div className="bg-white rounded-3xl p-6 shadow-sm border border-divider/50">
        <h3 className="text-sm font-medium text-primary mb-6">Mood History (Last 7 Days)</h3>
        <div className="flex items-end justify-between h-32 px-2">
          {Array.from({ length: 7 }).map((_, index) => {
            const date = new Date();
            date.setDate(date.getDate() - (6 - index));
            const dayLabel = date.toLocaleDateString('en-US', { weekday: 'narrow' });
            
            // Find mood entry for this day
            const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            const dayEnd = new Date(dayStart);
            dayEnd.setDate(dayEnd.getDate() + 1);
            
            const dayMoods = moodHistory.filter(entry => {
              const entryDate = new Date(entry.created_at);
              return entryDate >= dayStart && entryDate < dayEnd;
            });
            
            // Calculate average mood for the day (mood_score is 1-5)
            const avgMood = dayMoods.length > 0
              ? dayMoods.reduce((sum, entry) => sum + entry.mood_score, 0) / dayMoods.length
              : 0;
            
            // Convert mood score (1-5) to bar height (0-100%)
            const height = avgMood > 0 ? (avgMood / 5) * 100 : 0;
            
            return (
              <div key={index} className="flex flex-col items-center space-y-2">
                <div 
                  className={`w-2 rounded-full transition-all ${avgMood > 0 ? 'bg-sage' : 'bg-secondary/20'}`}
                  style={{ height: `${Math.max(height, 8)}%` }}
                  title={avgMood > 0 ? `Mood: ${avgMood.toFixed(1)}/5` : 'No data'}
                />
                <span className="text-[10px] text-secondary">
                  {dayLabel}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Safety Plan Modal */}
      <SafetyPlanModal 
        isOpen={showSafetyPlan} 
        onClose={() => setShowSafetyPlan(false)} 
      />
    </div>;
}