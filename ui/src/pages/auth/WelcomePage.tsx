import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { User, ArrowRight } from 'lucide-react';
import { apiClient } from '../../api/client';

interface WelcomePageProps {
  onNavigate: (page: 'signup' | 'login' | 'app') => void;
}

export function WelcomePage({
  onNavigate
}: WelcomePageProps) {
  const [isCreatingSession, setIsCreatingSession] = useState(false);

  const handleAnonymousContinue = async () => {
    try {
      setIsCreatingSession(true);
      await apiClient.createAnonymousSession();
      onNavigate('app');
    } catch (error) {
      console.error('Failed to create anonymous session:', error);
      alert('Failed to create session. Please try again.');
    } finally {
      setIsCreatingSession(false);
    }
  };

  return <AuthLayout>
      <div className="space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-light text-primary mb-2">
            Welcome to Dala
          </h2>
          <p className="text-secondary">
            A safe place to pause and feel heard.
          </p>
        </div>

        <button 
          onClick={handleAnonymousContinue}
          disabled={isCreatingSession}
          className="w-full bg-sage text-white py-4 rounded-xl font-medium shadow-sm hover:bg-sage-hover transition-all flex items-center justify-center space-x-2 group disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>{isCreatingSession ? 'Creating session...' : 'Continue Anonymously'}</span>
          {!isCreatingSession && (
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          )}
        </button>

        <div className="relative py-2">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-divider/50"></div>
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-subtle">
              Or create an account
            </span>
          </div>
        </div>

        <button onClick={() => onNavigate('signup')} className="w-full bg-white border border-divider text-primary py-3.5 rounded-xl font-medium hover:border-sage/50 hover:bg-background transition-all">
          Sign Up
        </button>

        <div className="text-center mt-4">
          <p className="text-sm text-secondary">
            Already have an account?{' '}
            <button onClick={() => onNavigate('login')} className="text-sage font-medium hover:underline">
              Log In
            </button>
          </p>
        </div>
      </div>
    </AuthLayout>;
}