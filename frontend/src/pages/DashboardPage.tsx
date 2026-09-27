import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Award,
  BarChart2,
  Bookmark,
  Briefcase,
  CheckCircle2,
  ChevronRight,
  Compass,
  FileText,
  Flame,
  RefreshCw,
  Sparkles,
  TrendingUp,
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
import { JobCard } from '../components/JobCard';
import { useAuth } from '../context/AuthContext';
import { Profile, Recommendation, Resume } from '../types';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [savedCount, setSavedCount] = useState<number>(0);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadDashboardData = async (forceRecompute: boolean = false) => {
    try {
      const [profData, recData, savedData, resumeData] = await Promise.all([
        api.getProfile().catch(() => null),
        api.getRecommendations(6, forceRecompute).catch(() => []),
        api.getSavedJobs().catch(() => []),
        api.getResumes().catch(() => []),
      ]);

      if (profData) setProfile(profData);
      if (recData) setRecommendations(recData);
      if (savedData) setSavedCount(savedData.length);
      if (resumeData) setResumes(resumeData);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadDashboardData(true);
  };

  const topMatch = recommendations.length > 0 ? Math.round(recommendations[0].overall_score) : 0;
  const avgMatch =
    recommendations.length > 0
      ? Math.round(
          recommendations.reduce((acc, curr) => acc + curr.overall_score, 0) /
            recommendations.length
        )
      : 0;

  // Chart data: Distribution of recommended matches
  const matchBins = [
    { range: '90-100%', count: recommendations.filter((r) => r.overall_score >= 90).length },
    { range: '80-89%', count: recommendations.filter((r) => r.overall_score >= 80 && r.overall_score < 90).length },
    { range: '70-79%', count: recommendations.filter((r) => r.overall_score >= 70 && r.overall_score < 80).length },
    { range: '60-69%', count: recommendations.filter((r) => r.overall_score >= 60 && r.overall_score < 70).length },
    { range: '<60%', count: recommendations.filter((r) => r.overall_score < 60).length },
  ];

  const hasResume = resumes.length > 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel relative overflow-hidden bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/20">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>Unified AI Discovery Hub</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Hello, {profile?.full_name || user?.email.split('@')[0]}!
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-xl">
              {hasResume
                ? 'Your resume has been parsed by NLP. Here are your ranked job recommendations and market skill alignment.'
                : 'Upload your resume to activate 5-factor AI matching and unlock personalized skill gap roadmaps.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold border border-slate-700 transition"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Recalculate AI Matches</span>
            </button>
            {!hasResume && (
              <Link
                to="/resume"
                className="px-5 py-2.5 rounded-xl gradient-bg font-bold text-sm text-white shadow-lg shadow-indigo-600/30 hover:opacity-95 transition"
              >
                Upload Resume
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">Highest Match</span>
            <div className="text-2xl font-extrabold text-emerald-400 mt-1">
              {topMatch > 0 ? `${topMatch}%` : 'N/A'}
            </div>
            <span className="text-[11px] text-slate-500 mt-0.5 block">Top role alignment</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <Award className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">Recommendations</span>
            <div className="text-2xl font-extrabold text-indigo-400 mt-1">
              {recommendations.length}
            </div>
            <span className="text-[11px] text-slate-500 mt-0.5 block">Ranked by algorithm</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
            <Sparkles className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">Saved Jobs</span>
            <div className="text-2xl font-extrabold text-purple-400 mt-1">{savedCount}</div>
            <span className="text-[11px] text-slate-500 mt-0.5 block">Tracked applications</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
            <Bookmark className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium block">Average Match</span>
            <div className="text-2xl font-extrabold text-blue-400 mt-1">
              {avgMatch > 0 ? `${avgMatch}%` : 'N/A'}
            </div>
            <span className="text-[11px] text-slate-500 mt-0.5 block">Across top 20 postings</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Match score distribution */}
        <div className="lg:col-span-2 p-6 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-indigo-400" />
                Match Score Distribution
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Number of harvested jobs in each compatibility bracket
              </p>
            </div>
            <span className="text-xs font-mono text-slate-500">Live Analytics</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={matchBins} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="range" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    color: '#f8fafc',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {matchBins.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        index === 0
                          ? '#10b981'
                          : index === 1
                          ? '#6366f1'
                          : index === 2
                          ? '#8b5cf6'
                          : index === 3
                          ? '#f59e0b'
                          : '#64748b'
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Action card */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between bg-gradient-to-br from-slate-900 to-indigo-950/20">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 mb-3">
              <Compass className="w-5 h-5" />
              <span className="text-xs font-bold uppercase tracking-wider">Career Assistant</span>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Accelerate Your Match Score</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Explore your Skill Gap report to uncover the high-frequency tools requested in top
              postings that you can add to your stack.
            </p>

            <div className="space-y-2 mb-6">
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Resume NLP parsed: {hasResume ? 'Yes' : 'Pending'}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Preferences set: {profile ? 'Yes' : 'Incomplete'}</span>
              </div>
            </div>
          </div>

          <Link
            to="/skill-gap"
            className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-semibold text-xs text-white text-center transition shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2"
          >
            <span>Analyze Skill Gaps</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Top Recommendations Feed */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              Top AI Recommendations
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Ranked dynamically by your skills, experience, degree, and semantic fit
            </p>
          </div>
          <Link
            to="/recommendations"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <span>View All ({recommendations.length})</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.slice(0, 4).map((rec) => (
              <JobCard
                key={rec.id}
                job={rec.job}
                matchScore={rec.overall_score}
                explanation={rec.explanation}
              />
            ))}
          </div>
        ) : (
          <div className="p-12 text-center rounded-2xl glass-panel border border-slate-800">
            <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">No recommendations yet</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto mb-4">
              Upload your resume so our NLP pipeline can extract your skills and calculate matching
              scores against active job postings.
            </p>
            <Link
              to="/resume"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl gradient-bg font-semibold text-xs text-white shadow-md shadow-indigo-600/30"
            >
              Upload Resume Now
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
