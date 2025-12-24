import React, { useState } from 'react';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { PrivacyConsent } from '../../components/auth/PrivacyConsent';
import { Eye, EyeOff, RefreshCw } from 'lucide-react';
import { apiClient } from '../../api/client';

interface SignupPageProps {
  onNavigate: (page: 'welcome' | 'login' | 'app') => void;
}

export function SignupPage({
  onNavigate
}: SignupPageProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [nickname, setNickname] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [consentGiven, setConsentGiven] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const suggestions = ['GentleRain', 'QuietSoul', 'CalmWaters', 'SoftBreeze'];

  const handleSuggestion = () => {
    const random = suggestions[Math.floor(Math.random() * suggestions.length)];
    setNickname(random);
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Register with correct parameter order: username, email, password
      await apiClient.register(nickname, email || '', password);
      onNavigate('app');
    } catch (err: any) {
      console.error('Signup failed:', err);
      // Handle Pydantic validation errors (array of objects) or string errors
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(e => e.msg).join(', '));
      } else {
        setError(detail || 'Signup failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return <AuthLayout title="Create Account" subtitle="Join our supportive community." onBack={() => onNavigate('welcome')}>
      <form className="space-y-6" onSubmit={handleSignup}>
        {/* Nickname */}
        <div>
          <label className="block text-sm font-medium text-primary mb-2">
            Nickname <span className="text-sage">*</span>
          </label>
          <div className="relative">
            <input type="text" value={nickname} onChange={e => setNickname(e.target.value)} placeholder="e.g. GentleRain" className="w-full bg-background border border-divider rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" required />
            <button type="button" onClick={handleSuggestion} className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-sage transition-colors" title="Generate random nickname">
              <RefreshCw size={16} />
            </button>
          </div>
          <p className="text-xs text-secondary mt-1.5">
            This is how you'll appear to others. You can change it later.
          </p>
        </div>

        {/* Password */}
        <div>
          <label className="block text-sm font-medium text-primary mb-2">
            Password <span className="text-sage">*</span>
          </label>
          <div className="relative">
            <input 
              type={showPassword ? 'text' : 'password'} 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min. 8 characters" 
              className="w-full bg-background border border-divider rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" 
              required 
              minLength={8}
              disabled={isLoading}
            />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors">
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        {/* Optional Email */}
        <div>
          <div className="flex justify-between items-baseline mb-2">
            <label className="block text-sm font-medium text-primary">
              Email
            </label>
            <span className="text-xs text-secondary italic">(Optional)</span>
          </div>
          <input 
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="For account recovery only" 
            className="w-full bg-background border border-divider rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all" 
            disabled={isLoading}
          />
        </div>

        {/* Optional Demographics */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-primary mb-2">
              Age{' '}
              <span className="text-xs text-secondary font-normal">
                (Optional)
              </span>
            </label>
            <select className="w-full bg-background border border-divider rounded-xl px-3 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all text-secondary">
              <option value="">Select...</option>
              <option value="18-24">18-24</option>
              <option value="25-34">25-34</option>
              <option value="35-44">35-44</option>
              <option value="45+">45+</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-primary mb-2">
              Gender{' '}
              <span className="text-xs text-secondary font-normal">
                (Optional)
              </span>
            </label>
            <select className="w-full bg-background border border-divider rounded-xl px-3 py-3 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all text-secondary">
              <option value="">Select...</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="non-binary">Non-binary</option>
              <option value="prefer-not-say">Prefer not to say</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}

        <PrivacyConsent checked={consentGiven} onChange={setConsentGiven} />

        <button type="submit" disabled={!consentGiven || !nickname || !password || isLoading} className="w-full bg-sage text-white py-3.5 rounded-xl font-medium shadow-sm hover:bg-sage-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all">
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>

        <div className="text-center">
          <p className="text-sm text-secondary">
            Already have an account?{' '}
            <button type="button" onClick={() => onNavigate('login')} className="text-sage font-medium hover:underline" disabled={isLoading}>
              Log In
            </button>
          </p>
        </div>
      </form>
    </AuthLayout>;
}