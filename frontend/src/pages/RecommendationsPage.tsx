import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Award,
  FileText,
  RefreshCw,
  Sliders,
  Sparkles,
  UploadCloud,
} from 'lucide-react';
import { api } from '../api/client';
import { JobCard } from '../components/JobCard';
import { Recommendation } from '../types';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [minScore, setMinScore] = useState<number>(40);
  const [loading, setLoading] = useState<boolean>(true);
  const [recomputing, setRecomputing] = useState<boolean>(false);

  const fetchRecommendations = async (recompute: boolean = false) => {
    if (recompute) setRecomputing(true);
    else setLoading(true);

    try {
      const data = await api.getRecommendations(30, recompute);
      setRecommendations(Array.isArray(data) ? data : []);
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
    <div className="animate-fade-in max-w-7xl mx-auto" style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
      {/* Header Banner — clean white theme */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-md)',
        }}
      >
        {/* Top section */}
        <div className="p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold mb-2"
                style={{
                  background: 'var(--color-primary-light)',
                  border: '1px solid var(--color-primary-border)',
                  color: 'var(--color-primary)',
                }}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Multi-Factor AI Ranking</span>
              </div>
              <h1 className="text-2xl font-extrabold" style={{ color: 'var(--color-text)' }}>
                Personalized Job Recommendations
              </h1>
              <p className="text-xs mt-1 max-w-2xl" style={{ color: 'var(--color-text-muted)' }}>
                Ranked by skills, semantic similarity, experience, degree, and career preferences.
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={() => fetchRecommendations(true)}
                disabled={recomputing}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-xs text-white transition hover:opacity-90 gradient-bg"
                style={{
                  boxShadow: '0 2px 12px rgba(19,102,214,0.25)',
                }}
              >
                <RefreshCw className={`w-3.5 h-3.5 ${recomputing ? 'animate-spin' : ''}`} />
                <span>{recomputing ? 'Re-scoring Jobs...' : 'Re-calculate Matches'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Filter bar */}
        <div
          className="px-6 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
          style={{
            borderTop: '1px solid var(--color-border)',
            background: 'var(--color-surface-hover)',
          }}
        >
          <div className="flex items-center gap-4 w-full sm:w-auto">
            <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
              <Sliders className="w-3.5 h-3.5" style={{ color: 'var(--color-primary)' }} />
              <span>Min Match Score:</span>
              <span className="font-bold font-mono" style={{ color: 'var(--color-primary)' }}>
                {minScore}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="90"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-36 cursor-pointer"
              style={{ accentColor: 'var(--color-primary)' }}
            />
          </div>

          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            Showing{' '}
            <strong style={{ color: 'var(--color-text)' }}>{filteredRecs.length}</strong> matching roles
          </span>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="p-16 text-center mt-4">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2" style={{ color: 'var(--color-primary)' }} />
          <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            Computing AI compatibility scores across catalog...
          </p>
        </div>
      ) : filteredRecs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
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
        <div
          className="p-12 text-center rounded-2xl mt-4"
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div
            className="w-14 h-14 rounded-2xl mx-auto flex items-center justify-center mb-3"
            style={{
              background: 'var(--color-surface-hover)',
              color: 'var(--color-text-muted)',
            }}
          >
            <Award className="w-7 h-7" />
          </div>
          <h3 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
            No roles met the threshold ({minScore}%)
          </h3>
          <p className="text-xs mt-1 mb-5 max-w-md mx-auto" style={{ color: 'var(--color-text-muted)' }}>
            Lower the minimum score slider or upload a resume to extract more skills and boost your match scores.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={() => setMinScore(0)}
              className="px-4 py-2 rounded-xl text-xs font-semibold transition"
              style={{
                background: 'var(--color-surface-hover)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Reset Threshold to 0%
            </button>
            <Link
              to="/resume"
              className="px-4 py-2 rounded-xl gradient-bg text-xs font-semibold text-white transition hover:opacity-95 flex items-center gap-1.5"
              style={{ boxShadow: '0 2px 8px rgba(19,102,214,0.25)' }}
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Upload / Update Resume</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};
