import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Bookmark,
  Briefcase,
  Compass,
  FileText,
  LayoutDashboard,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  User,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/recommendations', label: 'AI Recommendations', icon: Sparkles, highlight: true },
    { to: '/jobs', label: 'Explore Jobs', icon: Briefcase },
    { to: '/skill-gap', label: 'Skill Gap Analyzer', icon: TrendingUp },
    { to: '/resume', label: 'Resume & NLP', icon: FileText },
    { to: '/saved', label: 'Saved Applications', icon: Bookmark },
    { to: '/profile', label: 'Profile & Preferences', icon: User },
  ];

  if (user?.is_admin) {
    links.push({ to: '/admin', label: 'Admin Ingestion', icon: ShieldAlert, highlight: false });
  }

  return (
    <aside className="w-64 shrink-0 hidden lg:block border-r border-slate-800/80 bg-slate-950/40 p-4 min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{link.label}</span>
              </div>
              {link.highlight && (
                <span className="w-2 h-2 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500" />
              )}
            </NavLink>
          );
        })}
      </div>

      {/* AI Assistant Tip Card */}
      <div className="mt-8 p-4 rounded-2xl glass-panel border border-indigo-500/20 bg-gradient-to-b from-indigo-950/20 to-slate-900/60">
        <div className="flex items-center gap-2 mb-1.5">
          <Compass className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-300">
            Pro Tip
          </span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Upload your resume in PDF format to automatically extract 25+ skills and boost job matching precision.
        </p>
      </div>
    </aside>
  );
};
