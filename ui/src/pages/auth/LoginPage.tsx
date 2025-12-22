import React, { useState } from 'react';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { Eye, EyeOff } from 'lucide-react';
import { apiClient } from '../../api/client';

interface LoginPageProps {
  onNavigate: (page: 'welcome' | 'signup' | 'app') => void;
}

export function LoginPage({
  onNavigate
}: LoginPageProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await apiClient.login(identifier, password);
      onNavigate('app');
    } catch (err: any) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnonymousContinue = async () => {
    setError('');
    setIsLoading(true);
    try {
      await apiClient.createAnonymousSession();
      onNavigate('app');
    } catch (err: any) {
      console.error('Failed to create anonymous session:', err);
      setError('Failed to continue. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return <AuthLayout title="Welcome Back" subtitle="Log in to continue your journey." onBack={() => onNavigate('welcome')}>
      <form className="space-y-6" onSubmit={handleLogin}>
        <div>
          <label className="block text-sm font-medium text-primary mb-2">
            Email or Nickname
          </label>
          <input 
            type="text" 
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            className="w-full bg-background border border-divider rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" 
            required 
            disabled={isLoading}
          />
        </div>

        <div>
          <div className="flex justify-between items-baseline mb-2">
            <label className="block text-sm font-medium text-primary">
              Password
            </label>
            <button type="button" className="text-xs text-sage hover:underline">
              Forgot password?
            </button>
          </div>
          <div className="relative">
            <input 
              type={showPassword ? 'text' : 'password'} 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background border border-divider rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" 
              required 
              disabled={isLoading}
            />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors">
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}

        <div className="flex items-center">
          <input type="checkbox" id="remember" className="w-4 h-4 rounded border-sage text-sage focus:ring-sage" />
          <label htmlFor="remember" className="ml-2 text-sm text-secondary">
            Remember me
          </label>
        </div>

        <button type="submit" className="w-full bg-sage text-white py-3.5 rounded-xl font-medium shadow-sm hover:bg-sage-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Log In'}
        </button>

        <div className="text-center space-y-4">
          <p className="text-sm text-secondary">
            Don't have an account?{' '}
            <button type="button" onClick={() => onNavigate('signup')} className="text-sage font-medium hover:underline" disabled={isLoading}>
              Sign Up
            </button>
          </p>

          <button type="button" onClick={handleAnonymousContinue} className="text-xs text-secondary hover:text-primary hover:underline" disabled={isLoading}>
            {isLoading ? 'Please wait...' : 'Continue without account'}
          </button>
        </div>
      </form>
    </AuthLayout>;
}