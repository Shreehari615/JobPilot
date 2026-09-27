import React from 'react';

interface Props {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const MatchScoreBadge: React.FC<Props> = ({ score, size = 'md', showLabel = false }) => {
  const rounded = Math.round(score);

  let colorClasses = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
  let glowColor = 'rgba(16, 185, 129, 0.2)';
  if (rounded < 50) {
    colorClasses = 'text-slate-400 bg-slate-500/10 border-slate-500/30';
    glowColor = 'rgba(148, 163, 184, 0.2)';
  } else if (rounded < 70) {
    colorClasses = 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    glowColor = 'rgba(245, 158, 11, 0.2)';
  } else if (rounded < 85) {
    colorClasses = 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30';
    glowColor = 'rgba(99, 102, 241, 0.2)';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 border rounded-full font-semibold',
    md: 'text-sm px-2.5 py-1 border rounded-lg font-bold',
    lg: 'text-lg px-4 py-2 border-2 rounded-xl font-extrabold',
  }[size];

  return (
    <div
      className={`inline-flex items-center gap-1.5 shadow-sm transition-all ${colorClasses} ${sizeClasses}`}
      style={{ boxShadow: `0 0 12px ${glowColor}` }}
    >
      <span>{rounded}%</span>
      {showLabel && <span className="font-normal text-xs opacity-80">Match</span>}
    </div>
  );
};
