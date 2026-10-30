import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Bot, Lock, Mail } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.login({ email, password });
      login(res.access_token, {
        id: res.user_id,
        email: res.email,
        is_active: true,
        is_admin: res.is_admin,
        created_at: new Date().toISOString(),
      });
      navigate('/jobs');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Invalid email or password. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 mesh-gradient-bg">
      <div
        className="w-full max-w-md p-8 rounded-3xl relative"
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div className="text-center mb-8">
          <div
            className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center mb-3"
            style={{
              background: 'var(--color-primary-light)',
              color: 'var(--color-primary)',
              boxShadow: '0 4px 16px -4px rgba(19,102,214,0.18)',
            }}
          >
            <Bot className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold" style={{ color: 'var(--color-text)' }}>
            Welcome Back
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>
            Sign in to your JobPilot AI account
          </p>
        </div>

        {error && (
          <div
            className="mb-6 p-3.5 rounded-xl text-xs flex items-center gap-2"
            style={{
              background: 'var(--color-error-light)',
              border: '1px solid #fecdca',
              color: '#b42318',
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Email Address
            </label>
            <div className="relative">
              <Mail
                className="w-4 h-4 absolute left-3.5 top-3"
                style={{ color: 'var(--color-text-muted)' }}
              />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                style={{
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border-strong)',
                  color: 'var(--color-text)',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          <div>
            <label
              className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Password
            </label>
            <div className="relative">
              <Lock
                className="w-4 h-4 absolute left-3.5 top-3"
                style={{ color: 'var(--color-text-muted)' }}
              />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition focus:outline-none"
                style={{
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border-strong)',
                  color: 'var(--color-text)',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--color-primary)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(19,102,214,0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--color-border-strong)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
            <div className="flex justify-end mt-1">
              <a
                href="/forgot-password"
                className="text-xs font-semibold hover:underline"
                style={{ color: 'var(--color-primary)' }}
              >
                Forgot password?
              </a>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl gradient-bg font-bold text-sm text-white transition flex items-center justify-center gap-2 hover:opacity-95"
            style={{ boxShadow: '0 4px 16px -4px rgba(19,102,214,0.35)' }}
          >
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-xs mt-6" style={{ color: 'var(--color-text-muted)' }}>
          Don't have an account yet?{' '}
          <Link
            to="/register"
            className="font-semibold hover:underline"
            style={{ color: 'var(--color-primary)' }}
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
};
