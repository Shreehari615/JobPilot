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

  // ── WEEK-2 DEMO: only Explore Jobs is visible ──────────────────────────
  const links: { to: string; label: string; icon: React.ElementType; highlight?: boolean }[] = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/recommendations', label: 'AI Recommendations', icon: Sparkles, highlight: true },
    { to: '/jobs', label: 'Explore Jobs', icon: Briefcase },
    // { to: '/skill-gap', label: 'Skill Gap Analyzer', icon: TrendingUp }, // hidden
    { to: '/resume', label: 'Resume & NLP', icon: FileText },
    // { to: '/saved', label: 'Saved Applications', icon: Bookmark },
    // { to: '/profile', label: 'Profile & Preferences', icon: User },
  ];

  // Admin link also hidden for demo
  // if (user?.is_admin) {
  //   links.push({ to: '/admin', label: 'Admin Ingestion', icon: ShieldAlert, highlight: false });
  // }

  return (
    <aside className="w-60 shrink-0 hidden lg:block border-r p-4 min-h-[calc(100vh-4rem)]"
      style={{ background: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <div className="space-y-0.5">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'font-semibold'
                    : ''
                }`
              }
              style={({ isActive }) => isActive
                ? { background: 'var(--color-primary-light)', color: 'var(--color-primary)' }
                : { color: 'var(--color-text-secondary)' }
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{link.label}</span>
              </div>
              {link.highlight && (
                <span className="w-2 h-2 rounded-full" style={{ background: 'var(--color-primary)' }} />
              )}
            </NavLink>
          );
        })}
      </div>

      {/* AI Assistant Tip Card */}
      <div className="mt-6 p-4 rounded-xl" style={{ background: 'var(--color-primary-light)', border: '1px solid var(--color-primary-border)' }}>
        <div className="flex items-center gap-2 mb-1.5">
          <Compass className="w-4 h-4" style={{ color: 'var(--color-primary)' }} />
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--color-primary)' }}>
            Pro Tip
          </span>
        </div>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
          Upload your resume in PDF format to automatically extract 25+ skills and boost job matching precision.
        </p>
      </div>
    </aside>
  );
};
