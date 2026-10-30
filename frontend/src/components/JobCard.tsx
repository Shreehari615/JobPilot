import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { Bookmark, Building2, Calendar, ExternalLink, HelpCircle, MapPin, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { Explanation, Job } from '../types';
import { MatchScoreBadge } from './MatchScoreBadge';
import { ScoreBreakdownModal } from './ScoreBreakdownModal';
import { SkillTag } from './SkillTag';

interface Props {
  job: Job;
  matchScore?: number;
  explanation?: Explanation;
  isSaved?: boolean;
  onSaveToggle?: (jobId: number, saved: boolean) => void;
}

export const JobCard: React.FC<Props> = ({
  job,
  matchScore,
  explanation,
  isSaved = false,
  onSaveToggle,
}) => {
  const [saved, setSaved] = useState(isSaved);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    setSaving(true);
    try {
      if (saved) {
        await api.unsaveJob(job.id);
        setSaved(false);
        onSaveToggle?.(job.id, false);
      } else {
        await api.saveJob(job.id, 'saved');
        setSaved(true);
        onSaveToggle?.(job.id, true);
      }
    } catch (err) {
      console.error('Failed to update save status', err);
    } finally {
      setSaving(false);
    }
  };

  const handleApplyClick = () => {
    // Track click interaction
    api.trackInteraction(job.id, 'clicked_apply').catch(() => {});
    window.open(job.original_url, '_blank', 'noopener,noreferrer');
  };

  const formatSalary = () => {
    if (!job.salary_min && !job.salary_max) return 'Competitive / Undisclosed';
    const curr = job.salary_currency === 'INR' ? '₹' : job.salary_currency;
    const formatNum = (n: number) => {
      if (n >= 100000) return `${(n / 100000).toFixed(1)}L`;
      if (n >= 1000) return `${(n / 1000).toFixed(0)}k`;
      return n.toLocaleString();
    };
    if (job.salary_min && job.salary_max) {
      return `${curr}${formatNum(job.salary_min)} - ${curr}${formatNum(job.salary_max)}`;
    }
    if (job.salary_min) return `From ${curr}${formatNum(job.salary_min)}`;
    return `Up to ${curr}${formatNum(job.salary_max!)}`;
  };

  return (
    <>
      <div className="glass-panel glass-panel-hover rounded-2xl p-5 relative flex flex-col justify-between transition-all duration-200">
        <div>
          {/* Top header row */}
          <div className="flex items-start justify-between gap-4 mb-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full capitalize"
                  style={{ background: 'var(--color-surface-hover)', color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)' }}>
                  {job.work_mode || 'onsite'}
                </span>
                {job.job_type && (
                  <span className="text-xs font-medium px-2.5 py-0.5 rounded-full capitalize"
                    style={{ background: 'var(--color-primary-light)', color: 'var(--color-primary)', border: '1px solid var(--color-primary-border)' }}>
                    {job.job_type}
                  </span>
                )}
                {job.source_name && (
                  <span className="text-xs font-mono capitalize" style={{ color: 'var(--color-text-muted)' }}>
                    via {job.source_name}
                  </span>
                )}
                {!job.is_seed_data && (
                  <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1"
                    style={{ background: 'var(--color-success-light)', color: '#067647', border: '1px solid #abefc6' }}>
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Live Market
                  </span>
                )}
              </div>
              <h3 className="text-base font-bold transition-colors truncate"
                style={{ color: 'var(--color-text)' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'var(--color-primary)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--color-text)')}>
                {job.title}
              </h3>
              <div className="flex items-center gap-3 text-sm mt-1 flex-wrap" style={{ color: 'var(--color-text-secondary)' }}>
                <span className="flex items-center gap-1">
                  <Building2 className="w-3.5 h-3.5" />
                  {job.company || 'Confidential'}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {job.location || 'Remote'}
                </span>
              </div>
            </div>

            {/* Score and Save */}
            <div className="flex items-center gap-2 shrink-0">
              {matchScore !== undefined && (
                <div className="flex flex-col items-end">
                  <MatchScoreBadge score={matchScore} size="md" showLabel />
                  {explanation && (
                    <button
                      onClick={() => setShowModal(true)}
                      className="mt-1 flex items-center gap-1 text-[11px] underline underline-offset-2"
                      style={{ color: 'var(--color-primary)' }}
                    >
                      <Sparkles className="w-3 h-3" />
                      Why matched?
                    </button>
                  )}
                </div>
              )}
              <button
                onClick={handleSave}
                disabled={saving}
                className="p-2 rounded-xl border transition-all"
                style={saved
                  ? { background: 'var(--color-primary-light)', borderColor: 'var(--color-primary-border)', color: 'var(--color-primary)' }
                  : { background: 'var(--color-surface-hover)', borderColor: 'var(--color-border)', color: 'var(--color-text-muted)' }
                }
                title={saved ? 'Remove bookmark' : 'Bookmark job'}
              >
                <Bookmark className={`w-4 h-4 ${saved ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>

          {/* Description snippet */}
          {job.description && (
            <p className="text-sm line-clamp-2 mb-4 leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
              {job.description.replace(/<[^>]*>?/gm, '')}
            </p>
          )}

          {/* Skills required */}
          {job.skills && job.skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {job.skills.slice(0, 5).map((s, idx) => (
                <SkillTag
                  key={idx}
                  name={s.skill_name}
                  status={
                    explanation?.matched_skills?.includes(s.skill_name)
                      ? 'matching'
                      : explanation?.missing_skills?.includes(s.skill_name)
                      ? 'missing'
                      : 'default'
                  }
                />
              ))}
              {job.skills.length > 5 && (
                <span className="text-xs self-center px-1" style={{ color: 'var(--color-text-muted)' }}>
                  +{job.skills.length - 5} more
                </span>
              )}
            </div>
          )}
        </div>

        {/* Card Footer */}
        <div className="pt-3 border-t flex items-center justify-between mt-2 flex-wrap gap-2"
          style={{ borderColor: 'var(--color-border)' }}>
          <div>
            <span className="text-xs block" style={{ color: 'var(--color-text-muted)' }}>Compensation</span>
            <span className="text-sm font-semibold" style={{ color: 'var(--color-success)' }}>{formatSalary()}</span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={`https://www.google.com/search?q=${encodeURIComponent(`${job.company || ''} ${job.title} jobs`)}`}
              target="_blank"
              rel="noopener noreferrer"
              title="Search this job on Google Jobs / Company Careers"
              className="px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-all"
              style={{ background: 'var(--color-surface-hover)', color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)' }}
            >
              <span>Verify Opening</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <button
              onClick={handleApplyClick}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-semibold text-white transition-all hover:opacity-90 hover:scale-[1.02]"
              style={{ background: 'var(--color-primary)', boxShadow: '0 2px 8px rgba(19,102,214,0.22)' }}
            >
              <span>Apply on Site</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {showModal && ReactDOM.createPortal(
        <ScoreBreakdownModal
          job={job}
          score={matchScore || 0}
          explanation={explanation}
          onClose={() => setShowModal(false)}
        />,
        document.body
      )}
    </>
  );
};
