import React from 'react';
import { CheckCircle2, HelpCircle, XCircle } from 'lucide-react';

interface Props {
  name: string;
  status?: 'matching' | 'partial' | 'missing' | 'default';
  size?: 'sm' | 'md';
}

export const SkillTag: React.FC<Props> = ({ name, status = 'default', size = 'sm' }) => {
  const sizeClasses = size === 'sm' ? 'text-xs px-2.5 py-0.5' : 'text-sm px-3 py-1';

  let style: React.CSSProperties = {
    background: 'var(--color-surface-hover)',
    color: 'var(--color-text-secondary)',
    border: '1px solid var(--color-border)',
  };
  let icon = null;

  if (status === 'matching') {
    style = { background: 'var(--color-success-light)', color: '#067647', border: '1px solid #abefc6' };
    icon = <CheckCircle2 className="w-3.5 h-3.5 shrink-0" style={{ color: '#067647' }} />;
  } else if (status === 'partial') {
    style = { background: 'var(--color-warning-light)', color: '#b54708', border: '1px solid #fedf89' };
    icon = <HelpCircle className="w-3.5 h-3.5 shrink-0" style={{ color: '#b54708' }} />;
  } else if (status === 'missing') {
    style = { background: 'var(--color-error-light)', color: '#b42318', border: '1px solid #fecdca' };
    icon = <XCircle className="w-3.5 h-3.5 shrink-0" style={{ color: '#b42318' }} />;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium transition-colors ${sizeClasses}`}
      style={style}
    >
      {icon}
      <span>{name}</span>
    </span>
  );
};
