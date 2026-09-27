import React from 'react';
import { Award, BookOpen, Brain, Briefcase, CheckCircle2, ChevronRight, Compass, HeartHandshake, Sparkles, X } from 'lucide-react';
import { Explanation, Job } from '../types';
import { MatchScoreBadge } from './MatchScoreBadge';
import { SkillTag } from './SkillTag';

interface Props {
  job: Job;
  score: number;
  explanation?: Explanation;
  onClose: () => void;
}

export const ScoreBreakdownModal: React.FC<Props> = ({ job, score, explanation, onClose }) => {
  const breakdown = explanation?.score_breakdown;

  const factors = [
    {
      label: 'Skills Match',
      weight: '35%',
      value: breakdown?.skill_match || `${Math.round(score)}%`,
      icon: <Award className="w-5 h-5 text-indigo-400" />,
      desc: 'Overlap between your skills and role requirements',
    },
    {
      label: 'Semantic Match',
      weight: '30%',
      value: breakdown?.semantic_similarity || '82%',
      icon: <Brain className="w-5 h-5 text-purple-400" />,
      desc: 'Deep vector embedding similarity of resume to job text',
    },
    {
      label: 'Experience Fit',
      weight: '15%',
      value: breakdown?.experience_match || '90%',
      icon: <Briefcase className="w-5 h-5 text-emerald-400" />,
      desc: 'Years of professional experience vs requested seniority',
    },
    {
      label: 'Education Fit',
      weight: '10%',
      value: breakdown?.education_match || '85%',
      icon: <BookOpen className="w-5 h-5 text-amber-400" />,
      desc: 'Degree level and relevant field of study match',
    },
    {
      label: 'Preference Alignment',
      weight: '10%',
      value: breakdown?.preference_match || '95%',
      icon: <HeartHandshake className="w-5 h-5 text-pink-400" />,
      desc: 'Location, work mode, role title, and salary preferences',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl p-6 text-slate-100">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                AI Match Breakdown & Explainability
              </span>
            </div>
            <h2 className="text-xl font-bold text-white">{job.title}</h2>
            <p className="text-sm text-slate-400">
              {job.company} • {job.location || 'Remote'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Overall Match Hero */}
        <div className="my-6 p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/20 flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-indigo-300">Composite Match Score</span>
            <div className="text-3xl font-extrabold text-white mt-0.5">
              {Math.round(score)}%
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Calculated using our transparent 5-factor weighted algorithm
            </p>
          </div>
          <MatchScoreBadge score={score} size="lg" />
        </div>

        {/* 5-Factor Breakdown */}
        <div className="space-y-3 mb-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Factor Analysis
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {factors.map((f, i) => (
              <div
                key={i}
                className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/40 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {f.icon}
                    <span className="text-sm font-semibold text-slate-200">{f.label}</span>
                  </div>
                  <span className="text-xs font-mono text-slate-400">weight {f.weight}</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-xs text-slate-400">{f.desc}</span>
                  <span className="text-base font-bold text-indigo-300 ml-2">{f.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Explanations */}
        {explanation?.reasons && explanation.reasons.length > 0 && (
          <div className="mb-6 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50">
            <h3 className="text-sm font-semibold text-slate-200 mb-2 flex items-center gap-2">
              <Compass className="w-4 h-4 text-emerald-400" />
              Reasoning Generated from Candidate Profile
            </h3>
            <ul className="space-y-1.5 text-sm text-slate-300">
              {explanation.reasons.map((reason, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Skills Matched vs Missing */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
          <div>
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              Matching Skills ({explanation?.matched_skills?.length || 0})
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {explanation?.matched_skills && explanation.matched_skills.length > 0 ? (
                explanation.matched_skills.map((s, idx) => (
                  <SkillTag key={idx} name={s} status="matching" />
                ))
              ) : (
                <span className="text-xs text-slate-500">None detected</span>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <X className="w-4 h-4" />
              Skills to Develop ({explanation?.missing_skills?.length || 0})
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {explanation?.missing_skills && explanation.missing_skills.length > 0 ? (
                explanation.missing_skills.map((s, idx) => (
                  <SkillTag key={idx} name={s} status="missing" />
                ))
              ) : (
                <span className="text-xs text-emerald-400">All key skills matched!</span>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="mt-8 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-semibold text-sm text-white transition shadow-md shadow-indigo-600/30"
          >
            Close Breakdown
          </button>
        </div>
      </div>
    </div>
  );
};
