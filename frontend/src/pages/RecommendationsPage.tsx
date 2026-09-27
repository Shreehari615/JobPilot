import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Award,
  Compass,
  FileText,
  Filter,
  RefreshCw,
  Sliders,
  Sparkles,
} from 'lucide-react';
import { api } from '../api/client';
import { JobCard } from '../components/JobCard';
import { Recommendation } from '../types';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [minScore, setMinScore] = useState<number>(50);
  const [loading, setLoading] = useState<boolean>(true);
  const [recomputing, setRecomputing] = useState<boolean>(false);

  const fetchRecommendations = async (recompute: boolean = false) => {
    if (recompute) setRecomputing(true);
    else setLoading(true);

    try {
      const data = await api.getRecommendations(30, recompute);
      setRecommendations(data);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setLoading(false);
      setRecomputing(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const filteredRecs = recommendations.filter((r) => r.overall_score >= minScore);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 bg-gradient-to-r from-indigo-950/30 via-slate-900 to-purple-950/20">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>Multi-Factor AI Ranking</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">
              Personalized Job Recommendations
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Ranked dynamically by evaluating your extracted skills, vector semantic similarity,
              experience level, degree, and career preferences.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => fetchRecommendations(true)}
              disabled={recomputing}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl gradient-bg font-semibold text-xs text-white shadow-md shadow-indigo-600/20 hover:opacity-95 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${recomputing ? 'animate-spin' : ''}`} />
              <span>{recomputing ? 'Re-scoring Jobs...' : 'Re-calculate Matches'}</span>
            </button>
          </div>
        </div>

        {/* Filter bar */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4 w-full sm:w-auto">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Sliders className="w-3.5 h-3.5 text-indigo-400" />
              <span>Minimum Match Score:</span>
              <span className="font-bold text-white font-mono">{minScore}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="90"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-32 accent-indigo-500 cursor-pointer"
            />
          </div>

          <span className="text-xs text-slate-400">
            Showing <strong className="text-white">{filteredRecs.length}</strong> matching roles
          </span>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="p-16 text-center">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-2" />
          <p className="text-xs text-slate-400">Computing AI compatibility scores...</p>
        </div>
      ) : filteredRecs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredRecs.map((rec) => (
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
          <Award className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No roles met the threshold ({minScore}%)</h3>
          <p className="text-xs text-slate-400 mt-1 mb-4">
            Lower the minimum score slider or upload an updated resume with more skills.
          </p>
          <button
            onClick={() => setMinScore(0)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700"
          >
            Reset Threshold to 0%
          </button>
        </div>
      )}
    </div>
  );
};
