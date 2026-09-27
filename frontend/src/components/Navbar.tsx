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
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-white">JobPilot</span>
              <span className="px-1.5 py-0.2 text-[10px] font-bold rounded bg-indigo-500 text-white uppercase tracking-wider">
                AI
              </span>
            </div>
            <span className="text-[10px] text-slate-400 block -mt-1">
              Unified Career Discovery
            </span>
          </div>
        </Link>

        {/* Global AI status tag */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>MiniLM-L6 Semantic Engine Active</span>
        </div>

        {/* User actions */}
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <Link
                to="/profile"
                className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition"
              >
                <div className="w-7 h-7 rounded-lg bg-indigo-600/30 text-indigo-400 flex items-center justify-center text-xs font-bold">
                  {user?.email[0].toUpperCase()}
                </div>
                <div className="hidden sm:block text-left text-xs">
                  <div className="font-medium text-white truncate max-w-[120px]">
                    {user?.email.split('@')[0]}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {user?.is_admin ? 'Admin' : 'Candidate'}
                  </div>
                </div>
              </Link>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-xl transition"
                title="Log out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 transition"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="text-sm font-semibold px-4 py-2 rounded-xl gradient-bg text-white shadow-md shadow-indigo-600/20 hover:opacity-95 transition"
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
