import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { BottomNav, TabId } from './components/BottomNav';
import { HomeTab } from './pages/HomeTab';
import { CompanionTab } from './pages/CompanionTab';
import { PathsTab } from './pages/PathsTab';
import { CirclesTab } from './pages/CirclesTab';
import { ProfileTab } from './pages/ProfileTab';
import { AdminLayout } from './components/admin/AdminLayout';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { UserManagement } from './pages/admin/UserManagement';
import { ContentModeration } from './pages/admin/ContentModeration';
import { SystemMonitoring } from './pages/admin/SystemMonitoring';
import { CircleManagement } from './pages/admin/CircleManagement';
import { PathManagement } from './pages/admin/PathManagement';
import { SafetyManagement } from './pages/admin/SafetyManagement';
import { Analytics } from './pages/admin/Analytics';
import { WelcomePage } from './pages/auth/WelcomePage';
import { SignupPage } from './pages/auth/SignupPage';
import { LoginPage } from './pages/auth/LoginPage';
import { apiClient } from './api/client';

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>(() => {
    const saved = localStorage.getItem('activeTab');
    return (saved as TabId) || 'home';
  });
  const [isAdminMode, setIsAdminMode] = useState(() => {
    const saved = localStorage.getItem('isAdminMode');
    return saved === 'true';
  });
  const [adminPage, setAdminPage] = useState(() => {
    const saved = localStorage.getItem('adminPage');
    return saved || 'dashboard';
  });
  // Auth State
  const [authMode, setAuthMode] = useState<'welcome' | 'signup' | 'login' | 'app'>('welcome');
  const [isInitializing, setIsInitializing] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [username, setUsername] = useState<string>('');

  // Persist active tab to localStorage
  useEffect(() => {
    localStorage.setItem('activeTab', activeTab);
  }, [activeTab]);

  // Persist admin mode to localStorage
  useEffect(() => {
    localStorage.setItem('isAdminMode', isAdminMode.toString());
  }, [isAdminMode]);

  // Persist admin page to localStorage
  useEffect(() => {
    localStorage.setItem('adminPage', adminPage);
  }, [adminPage]);

  // Check if user has existing token on app start
  useEffect(() => {
    const initializeSession = async () => {
      try {
        const existingToken = apiClient.getToken();
        if (existingToken) {
          // Validate token by trying to fetch profile
          try {
            const profile = await apiClient.getProfile();
            console.log('Valid session found');
            console.log('Profile is_admin:', profile.is_admin);
            console.log('Profile role:', profile.role);
            console.log('Setting isAdmin to:', profile.is_admin || false);
            setIsAdmin(profile.is_admin || false);
            setUsername(profile.username || '');
            setAuthMode('app');
          } catch (error) {
            // Invalid token, clear it
            console.log('Invalid token, clearing session');
            apiClient.clearAuth();
            setAuthMode('welcome');
          }
        } else {
          // No session, show welcome page
          console.log('No session found, showing welcome page');
          setAuthMode('welcome');
        }
      } catch (error) {
        console.error('Failed to initialize session:', error);
        apiClient.clearAuth();
        setAuthMode('welcome');
      } finally {
        setIsInitializing(false);
      }
    };
    initializeSession();
  }, []);

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-sage text-sm">Initializing...</div>
      </div>
    );
  }
  const renderTab = () => {
    switch (activeTab) {
      case 'home':
        return <HomeTab onNavigate={tab => setActiveTab(tab)} onLogout={handleLogout} username={username} />;
      case 'companion':
        return <CompanionTab />;
      case 'paths':
        return <PathsTab />;
      case 'circles':
        return <CirclesTab />;
      case 'profile':
        return <div className="relative">
            <ProfileTab onLogout={handleLogout} />
            {/* Admin Toggle - Only visible for admin users */}
            {isAdmin && (
              <button onClick={() => setIsAdminMode(true)} className="fixed bottom-24 right-6 bg-primary text-white text-xs px-3 py-1 rounded-full opacity-50 hover:opacity-100 transition-opacity">
                Admin Mode
              </button>
            )}
          </div>;
      default:
        return <HomeTab onNavigate={tab => setActiveTab(tab)} />;
    }
  };

  const handleLogout = () => {
    apiClient.logout();
    setIsAdmin(false);
    setUsername('');
    setAuthMode('welcome');
    setActiveTab('home');
  };
  const renderAdminPage = () => {
    switch (adminPage) {
      case 'dashboard':
        return <AdminDashboard onNavigate={setAdminPage} />;
      case 'users':
        return <UserManagement />;
      case 'moderation':
        return <ContentModeration />;
      case 'system':
        return <SystemMonitoring />;
      case 'circles':
        return <CircleManagement />;
      case 'paths':
        return <PathManagement />;
      case 'safety':
        return <SafetyManagement />;
      case 'analytics':
        return <Analytics />;
      default:
        return <AdminDashboard onNavigate={setAdminPage} />;
    }
  };
  // Auth Flow Handling
  if (authMode === 'welcome') {
    return <WelcomePage onNavigate={setAuthMode} />;
  }
  if (authMode === 'signup') {
    return <SignupPage onNavigate={setAuthMode} />;
  }
  if (authMode === 'login') {
    return <LoginPage onNavigate={setAuthMode} />;
  }
  // Admin Mode Handling
  if (isAdminMode) {
    return <AdminLayout activePage={adminPage} onNavigate={setAdminPage} onLogout={() => setIsAdminMode(false)}>
        {renderAdminPage()}
      </AdminLayout>;
  }
  // Main App
  return <div className="min-h-screen w-full bg-background selection:bg-sage/20 font-sans">
      <main className="min-h-screen pb-20">
        <AnimatePresence mode="wait">{renderTab()}</AnimatePresence>
      </main>

      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>;
}