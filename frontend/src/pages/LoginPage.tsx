import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Bot, Lock, Mail, Sparkles } from 'lucide-react';
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
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Invalid email or password. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (role: 'user' | 'admin') => {
    if (role === 'admin') {
      setEmail('admin@jobpilot.ai');
      setPassword('AdminPass123!');
    } else {
      setEmail('candidate@jobpilot.ai');
      setPassword('CandidatePass123!');
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 mesh-gradient-bg">
      <div className="w-full max-w-md p-8 rounded-3xl glass-panel border border-slate-800/80 shadow-2xl relative">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl gradient-bg mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/20 mb-3">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold text-white">Welcome Back</h2>
          <p className="text-sm text-slate-400 mt-1">Sign in to your JobPilot AI account</p>
        </div>

        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl gradient-bg font-bold text-sm text-white shadow-lg shadow-indigo-600/30 hover:opacity-95 transition flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo login shortcuts for convenience */}
        <div className="mt-6 pt-6 border-t border-slate-800">
          <span className="block text-center text-xs text-slate-500 mb-2">
            Quick demo credentials:
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleDemoFill('user')}
              className="flex-1 py-1.5 px-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs hover:border-indigo-500 transition"
            >
              Candidate Demo
            </button>
            <button
              type="button"
              onClick={() => handleDemoFill('admin')}
              className="flex-1 py-1.5 px-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs hover:border-indigo-500 transition"
            >
              Admin Demo
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          Don't have an account yet?{' '}
          <Link to="/register" className="text-indigo-400 font-semibold hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
};
