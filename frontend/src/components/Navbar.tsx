import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bot, LogOut, Search, Sparkles, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white" style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-sm)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center" style={{ boxShadow: '0 4px 12px rgba(19,102,214,0.25)' }}>
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight" style={{ color: 'var(--color-text)' }}>JobPilot</span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold rounded" style={{ background: 'var(--color-primary)', color: '#fff', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                AI
              </span>
            </div>
            <span className="text-[10px] block -mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
              Unified Career Discovery
            </span>
          </div>
        </Link>

        {/* Global AI status tag */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium" style={{ background: 'var(--color-primary-light)', border: '1px solid var(--color-primary-border)', color: 'var(--color-primary)' }}>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>MiniLM-L6 Semantic Engine Active</span>
        </div>

        {/* User actions */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <Link
                to="/profile"
                className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition"
                style={{ background: 'var(--color-surface-hover)', border: '1px solid var(--color-border)' }}
              >
                <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white" style={{ background: 'var(--color-primary)' }}>
                  {user?.email[0].toUpperCase()}
                </div>
                <div className="hidden sm:block text-left text-xs">
                  <div className="font-semibold truncate max-w-[120px]" style={{ color: 'var(--color-text)' }}>
                    {user?.email.split('@')[0]}
                  </div>
                  <div className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>
                    {user?.is_admin ? 'Admin' : 'Candidate'}
                  </div>
                </div>
              </Link>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg transition"
                style={{ color: 'var(--color-text-muted)' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'var(--color-error)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--color-text-muted)')}
                title="Log out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm font-medium px-3 py-1.5 rounded-lg transition"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="text-sm font-semibold px-4 py-2 rounded-lg text-white gradient-bg transition hover:opacity-90"
                style={{ boxShadow: '0 2px 8px rgba(19,102,214,0.25)' }}
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
