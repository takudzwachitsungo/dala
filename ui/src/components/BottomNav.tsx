import React from 'react';
import { motion } from 'framer-motion';
import { Home, MessageCircle, Map, Users, User } from 'lucide-react';
export type TabId = 'home' | 'companion' | 'paths' | 'circles' | 'profile';
interface BottomNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}
export function BottomNav({
  activeTab,
  onTabChange
}: BottomNavProps) {
  const tabs = [{
    id: 'home',
    label: 'Home',
    icon: Home
  }, {
    id: 'companion',
    label: 'Dala',
    icon: MessageCircle
  }, {
    id: 'paths',
    label: 'Paths',
    icon: Map
  }, {
    id: 'circles',
    label: 'Circles',
    icon: Users
  }, {
    id: 'profile',
    label: 'Profile',
    icon: User
  }] as const;
  return <div className="fixed bottom-0 left-0 right-0 bg-background/80 backdrop-blur-md border-t border-divider/50 pb-safe pt-2 z-50">
      <div className="max-w-md mx-auto px-6 h-16 flex items-center justify-between">
        {tabs.map(tab => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;
        return <button key={tab.id} onClick={() => onTabChange(tab.id)} className="relative flex flex-col items-center justify-center w-12 h-12 focus:outline-none group" aria-label={tab.label} aria-current={isActive ? 'page' : undefined}>
              <div className="relative">
                <Icon size={24} strokeWidth={isActive ? 2.5 : 1.5} className={`transition-colors duration-300 ${isActive ? 'text-sage' : 'text-secondary group-hover:text-primary'}`} />

                {isActive && <motion.div layoutId="nav-indicator" className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-sage" transition={{
              type: 'spring',
              stiffness: 500,
              damping: 30
            }} />}
              </div>

              <span className={`text-[10px] mt-1 font-medium transition-colors duration-300 ${isActive ? 'text-sage' : 'text-secondary'}`}>
                {tab.label}
              </span>
            </button>;
      })}
      </div>
    </div>;
}