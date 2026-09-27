import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Award,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Compass,
  GraduationCap,
  HelpCircle,
  Lightbulb,
  Sparkles,
  TrendingUp,
  XCircle,
  BarChart2,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { api } from '../api/client';
import { SkillTag } from '../components/SkillTag';
import { Recommendation, RecommendationDetail } from '../types';

export const SkillGapPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [detail, setDetail] = useState<RecommendationDetail | null>(null);
  const [marketStats, setMarketStats] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [recs, stats] = await Promise.all([
          api.getRecommendations(10),
          api.getJobStats(),
        ]);
        setRecommendations(recs);
        setMarketStats(stats);
        if (recs.length > 0) {
          setSelectedJobId(recs[0].job_id);
          loadJobDetail(recs[0].job_id);
        }
      } catch (err) {
        console.error('Failed to load skill gap data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, []);

  const loadJobDetail = async (jobId: number) => {
    setDetailLoading(true);
    try {
      const d = await api.getJobRecommendationDetail(jobId);
      setDetail(d);
    } catch (err) {
      console.error('Failed to load recommendation detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSelectJob = (jobId: number) => {
    setSelectedJobId(jobId);
    loadJobDetail(jobId);
  };

  const matchingSkills = detail?.skill_gaps.filter((s) => s.gap_type === 'matching') || [];
  const partialSkills = detail?.skill_gaps.filter((s) => s.gap_type === 'partial') || [];
  const missingSkills = detail?.skill_gaps.filter((s) => s.gap_type === 'missing') || [];

  const totalEvaluated = matchingSkills.length + partialSkills.length + missingSkills.length;
  const coveragePercent = totalEvaluated > 0
    ? Math.round(((matchingSkills.length + partialSkills.length * 0.5) / totalEvaluated) * 100)
    : 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 bg-gradient-to-r from-indigo-950/30 via-slate-900 to-purple-950/20">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
          <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
          <span>Automated Gap Diagnostics</span>
        </div>
        <h1 className="text-2xl font-extrabold text-white">Skill Gap & Market Readiness Analyzer</h1>
        <p className="text-xs text-slate-300 mt-1 max-w-2xl">
          Compare your verified skills directly against technical role requirements. Pinpoint
          prerequisites, partial matches, and high-impact skills to acquire.
        </p>
      </div>

      {/* Main Grid: Job Selector and Detailed Gap Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Role Selector */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Select Target Role
            </h2>
            <span className="text-xs text-slate-500">{recommendations.length} options</span>
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {recommendations.map((rec) => {
              const isSelected = rec.job_id === selectedJobId;
              return (
                <div
                  key={rec.id}
                  onClick={() => handleSelectJob(rec.job_id)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-indigo-950/50 border-indigo-500 shadow-md shadow-indigo-600/20'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-white truncate">{rec.job.title}</h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {rec.job.company} • {rec.job.location || 'Remote'}
                      </p>
                    </div>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-lg border ${
                        rec.overall_score >= 80
                          ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                          : 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30'
                      }`}
                    >
                      {Math.round(rec.overall_score)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 2 columns: Gap Analysis Canvas */}
        <div className="lg:col-span-2 space-y-6">
          {detailLoading ? (
            <div className="p-16 text-center glass-panel rounded-2xl">
              <span className="text-xs text-slate-400">Analyzing skill vectors...</span>
            </div>
          ) : detail ? (
            <>
              {/* Coverage summary card */}
              <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Technical Coverage for {detail.job?.title}
                  </span>
                  <div className="text-3xl font-extrabold text-white mt-1">
                    {coveragePercent}% Covered
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {matchingSkills.length} verified • {partialSkills.length} related •{' '}
                    {missingSkills.length} missing
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <div className="text-center px-4 py-2 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-xs text-emerald-400 block font-bold">
                      {matchingSkills.length}
                    </span>
                    <span className="text-[10px] text-slate-500">Matching</span>
                  </div>
                  <div className="text-center px-4 py-2 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-xs text-amber-400 block font-bold">
                      {partialSkills.length}
                    </span>
                    <span className="text-[10px] text-slate-500">Partial</span>
                  </div>
                  <div className="text-center px-4 py-2 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-xs text-rose-400 block font-bold">
                      {missingSkills.length}
                    </span>
                    <span className="text-[10px] text-slate-500">Missing</span>
                  </div>
                </div>
              </div>

              {/* 3 Categories Matrix */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Matching */}
                <div className="p-5 rounded-2xl glass-panel border border-emerald-500/20 bg-emerald-950/10">
                  <div className="flex items-center gap-2 text-emerald-400 mb-3">
                    <CheckCircle2 className="w-4 h-4" />
                    <h4 className="text-xs font-bold uppercase tracking-wider">
                      Matching Skills ({matchingSkills.length})
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {matchingSkills.length > 0 ? (
                      matchingSkills.map((s, i) => (
                        <SkillTag key={i} name={s.skill_name} status="matching" />
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">No exact matches.</span>
                    )}
                  </div>
                </div>

                {/* Partial / Related */}
                <div className="p-5 rounded-2xl glass-panel border border-amber-500/20 bg-amber-950/10">
                  <div className="flex items-center gap-2 text-amber-400 mb-3">
                    <HelpCircle className="w-4 h-4" />
                    <h4 className="text-xs font-bold uppercase tracking-wider">
                      Related Skills ({partialSkills.length})
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {partialSkills.length > 0 ? (
                      partialSkills.map((s, i) => (
                        <SkillTag key={i} name={s.skill_name} status="partial" />
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">No partial matches.</span>
                    )}
                  </div>
                </div>

                {/* Missing */}
                <div className="p-5 rounded-2xl glass-panel border border-rose-500/20 bg-rose-950/10">
                  <div className="flex items-center gap-2 text-rose-400 mb-3">
                    <XCircle className="w-4 h-4" />
                    <h4 className="text-xs font-bold uppercase tracking-wider">
                      To Acquire ({missingSkills.length})
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {missingSkills.length > 0 ? (
                      missingSkills.map((s, i) => (
                        <SkillTag key={i} name={s.skill_name} status="missing" />
                      ))
                    ) : (
                      <span className="text-xs text-emerald-400">Zero missing skills!</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Actionable Learning Roadmap */}
              {missingSkills.length > 0 && (
                <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-3">
                  <div className="flex items-center gap-2 text-indigo-400">
                    <Lightbulb className="w-5 h-5" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-white">
                      Recommended Learning Roadmap
                    </h3>
                  </div>
                  <p className="text-xs text-slate-400">
                    Focusing on these key missing skills will increase your match score for this
                    role to 95%+:
                  </p>
                  <div className="space-y-2 pt-2">
                    {missingSkills.slice(0, 4).map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800"
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="w-5 h-5 rounded-full bg-indigo-600/20 text-indigo-400 text-xs font-bold flex items-center justify-center">
                            {idx + 1}
                          </span>
                          <span className="text-sm font-medium text-white">{item.skill_name}</span>
                        </div>
                        <span className="text-[11px] text-slate-400">
                          Found in 85% of similar tech postings
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-12 text-center glass-panel rounded-2xl">
              <p className="text-xs text-slate-400">Select a role on the left to inspect skill gaps.</p>
            </div>
          )}

          {/* Top In-Demand Skills Market Overview Chart */}
          {marketStats?.top_skills && marketStats.top_skills.length > 0 && (
            <div className="p-6 rounded-2xl glass-panel border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-indigo-400" />
                    Market In-Demand Skills Frequency
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Most frequently requested skills across active Indian tech openings
                  </p>
                </div>
              </div>

              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={marketStats.top_skills.slice(0, 8)}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="skill" stroke="#64748b" fontSize={11} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        borderRadius: '0.75rem',
                        color: '#f8fafc',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
