import React, { useState } from 'react';
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
      <div className="glass-panel glass-panel-hover rounded-2xl p-6 relative flex flex-col justify-between transition-all duration-300">
        <div>
          {/* Top header row */}
          <div className="flex items-start justify-between gap-4 mb-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {job.work_mode || 'onsite'}
                </span>
                {job.job_type && (
                  <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-indigo-950/60 text-indigo-300 border border-indigo-500/20">
                    {job.job_type}
                  </span>
                )}
                {job.source_name && (
                  <span className="text-xs text-slate-500 font-mono capitalize">
                    via {job.source_name}
                  </span>
                )}
                {!job.is_seed_data && (
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Live Market
                  </span>
                )}
              </div>
              <h3 className="text-lg font-bold text-white hover:text-indigo-400 transition-colors truncate">
                {job.title}
              </h3>
              <div className="flex items-center gap-3 text-sm text-slate-400 mt-1 flex-wrap">
                <span className="flex items-center gap-1">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" />
                  {job.company || 'Confidential'}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
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
                      className="mt-1 flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
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
                className={`p-2 rounded-xl border transition-all ${
                  saved
                    ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-400'
                    : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-white hover:border-slate-500'
                }`}
                title={saved ? 'Remove bookmark' : 'Bookmark job'}
              >
                <Bookmark className={`w-4 h-4 ${saved ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>

          {/* Description snippet */}
          {job.description && (
            <p className="text-sm text-slate-300/80 line-clamp-2 mb-4 leading-relaxed">
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
                <span className="text-xs text-slate-500 self-center px-1">
                  +{job.skills.length - 5} more
                </span>
              )}
            </div>
          )}
        </div>

        {/* Card Footer */}
        <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between mt-2 flex-wrap gap-2">
          <div>
            <span className="text-xs text-slate-400 block">Compensation</span>
            <span className="text-sm font-semibold text-emerald-400">{formatSalary()}</span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={`https://www.google.com/search?q=${encodeURIComponent(`${job.company || ''} ${job.title} jobs`)}`}
              target="_blank"
              rel="noopener noreferrer"
              title="Search this job on Google Jobs / Company Careers"
              className="px-2.5 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 transition-all flex items-center gap-1"
            >
              <span>Verify Opening</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>
            <button
              onClick={handleApplyClick}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all hover:scale-[1.02]"
            >
              <span>Apply on Site</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {showModal && (
        <ScoreBreakdownModal
          job={job}
          score={matchScore || 0}
          explanation={explanation}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
};
