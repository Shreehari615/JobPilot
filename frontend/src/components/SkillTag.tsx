import React from 'react';
import { CheckCircle2, HelpCircle, XCircle } from 'lucide-react';

interface Props {
  name: string;
  status?: 'matching' | 'partial' | 'missing' | 'default';
  size?: 'sm' | 'md';
}

export const SkillTag: React.FC<Props> = ({ name, status = 'default', size = 'sm' }) => {
  const sizeClasses = size === 'sm' ? 'text-xs px-2.5 py-1' : 'text-sm px-3 py-1.5';

  let statusStyles = 'bg-slate-800/80 text-slate-300 border-slate-700/60 hover:border-slate-500';
  let icon = null;

  if (status === 'matching') {
    statusStyles = 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30';
    icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />;
  } else if (status === 'partial') {
    statusStyles = 'bg-amber-950/40 text-amber-300 border-amber-500/30';
    icon = <HelpCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
  } else if (status === 'missing') {
    statusStyles = 'bg-rose-950/40 text-rose-300 border-rose-500/30';
    icon = <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border font-medium transition-colors ${statusStyles} ${sizeClasses}`}
    >
      {icon}
      <span>{name}</span>
    </span>
  );
};
