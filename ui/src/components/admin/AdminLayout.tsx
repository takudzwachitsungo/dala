import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, Users, ShieldAlert, Activity, MessageCircle, HeartPulse, BarChart3, LogOut, Menu, X, BookOpen } from 'lucide-react';
interface AdminLayoutProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
  onLogout: () => void;
}
export function AdminLayout({
  children,
  activePage,
  onNavigate,
  onLogout
}: AdminLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const menuItems = [{
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard
  }, {
    id: 'users',
    label: 'User Management',
    icon: Users
  }, {
    id: 'moderation',
    label: 'Content Moderation',
    icon: ShieldAlert
  }, {
    id: 'system',
    label: 'System Monitoring',
    icon: Activity
  }, {
    id: 'circles',
    label: 'Circle Management',
    icon: MessageCircle
  }, {
    id: 'paths',
    label: 'Path Management',
    icon: BookOpen
  }, {
    id: 'safety',
    label: 'Safety & Crisis',
    icon: HeartPulse
  }, {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3
  }];
  return <div className="min-h-screen bg-background flex">
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex flex-col w-64 border-r border-divider/50 bg-white/50 backdrop-blur-sm fixed h-full z-20">
        <div className="p-6 border-b border-divider/50">
          <h1 className="text-xl font-light text-primary tracking-tight">
            Dala Admin
          </h1>
          <p className="text-xs text-secondary mt-1">Moderator Dashboard</p>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return <button key={item.id} onClick={() => onNavigate(item.id)} className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors ${isActive ? 'bg-sage/10 text-sage' : 'text-secondary hover:text-primary hover:bg-secondary/5'}`}>
                <Icon size={18} />
                <span>{item.label}</span>
              </button>;
        })}
        </nav>

        <div className="p-4 border-t border-divider/50">
          <button onClick={onLogout} className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50 transition-colors">
            <LogOut size={18} />
            <span>Exit Admin Mode</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 min-h-screen flex flex-col">
        {/* Mobile Header */}
        <header className="lg:hidden h-16 border-b border-divider/50 bg-white/80 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-30">
          <span className="font-medium text-primary">Dala Admin</span>
          <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-primary">
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </header>

        {/* Mobile Menu Overlay */}
        {isMobileMenuOpen && <div className="lg:hidden fixed inset-0 z-20 bg-background pt-16 px-4 pb-6 overflow-y-auto">
            <nav className="space-y-2">
              {menuItems.map(item => <button key={item.id} onClick={() => {
            onNavigate(item.id);
            setIsMobileMenuOpen(false);
          }} className={`w-full flex items-center space-x-3 px-4 py-4 rounded-xl text-sm font-medium ${activePage === item.id ? 'bg-sage/10 text-sage' : 'text-secondary'}`}>
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </button>)}
              <button onClick={onLogout} className="w-full flex items-center space-x-3 px-4 py-4 rounded-xl text-sm font-medium text-red-500 mt-4 border-t border-divider">
                <LogOut size={20} />
                <span>Exit Admin Mode</span>
              </button>
            </nav>
          </div>}

        {/* Page Content */}
        <div className="flex-1 p-6 lg:p-10 overflow-y-auto">{children}</div>
      </main>
    </div>;
}