import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Bot,
  Brain,
  Briefcase,
  CheckCircle,
  Compass,
  Cpu,
  FileCheck,
  Layers,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen mesh-gradient-bg flex flex-col">
      {/* Hero Section */}
      <section className="relative pt-20 pb-28 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">


          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight max-w-4xl mx-auto leading-tight sm:leading-none" style={{ color: 'var(--color-text)' }}>
            Unified AI Job Discovery & <span className="gradient-text">Smart Application</span> Assistant
          </h1>

          <p className="mt-6 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
            Eliminate random job boards. JobPilot AI parses your resume with NLP, calculates
            transparent 5-factor compatibility scores, and pinpoints exact skill gaps for every role.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to={isAuthenticated ? '/jobs' : '/login'}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-base text-white gradient-bg flex items-center justify-center gap-2 transition hover:opacity-90 hover:scale-105"
              style={{ boxShadow: '0 4px 16px rgba(19,102,214,0.28)' }}
            >
              <span>{isAuthenticated ? 'Explore Jobs' : 'Get Started Free'}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/jobs"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold text-base flex items-center justify-center gap-2 transition hover:opacity-90"
              style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border-strong)', color: 'var(--color-text-secondary)', boxShadow: 'var(--shadow-sm)' }}
            >
              <Search className="w-4 h-4" style={{ color: 'var(--color-primary)' }} />
              <span>Explore Active Jobs</span>
            </Link>
          </div>

          {/* ── WEEK-2 DEMO: Metrics summary bar — hidden ──────────────── */}
          {false && (
          <div className="mt-16 max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Skills in Taxonomy', value: '700+' },
              { label: 'Evaluation Factors', value: '5-Factor' },
              { label: 'Deduplication Depth', value: '3 Levels' },
              { label: 'Direct Apply', value: '100% Genuine' },
            ].map((stat, i) => (
              <div
                key={i}
                className="p-4 rounded-xl glass-panel border border-slate-800/80 text-center"
              >
                <div className="text-2xl sm:text-3xl font-extrabold text-white">{stat.value}</div>
                <div className="text-xs text-slate-400 mt-1 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
          )}
        </div>
      </section>

      {/* ── WEEK-2 DEMO: How It Works Pipeline — hidden ──────────────── */}
      {false && (
      <section className="py-20 border-t border-slate-800/80 bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
              End-to-End Pipeline
            </span>
            <h2 className="text-3xl font-extrabold text-white mt-2">
              How JobPilot AI Matches You With Real Jobs
            </h2>
            <p className="text-slate-400 mt-3 text-sm sm:text-base">
              No black-box algorithms or fake randomized numbers. Every recommendation is backed by
              verifiable NLP text parsing and mathematical cosine similarity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: '01',
                title: 'Resume NLP Extraction',
                desc: 'Upload PDF or DOCX. spaCy and NLTK extract skills, education, work duration, and canonicalize aliases.',
                icon: FileCheck,
              },
              {
                step: '02',
                title: 'Multi-Source Harvesting',
                desc: 'Aggregates listings from public APIs, legal scrapers, and verified tech hubs into one normalized schema.',
                icon: Layers,
              },
              {
                step: '03',
                title: '5-Factor AI Matching',
                desc: 'Weighs skills (35%), semantic vectors (30%), experience (15%), degree (10%), and personal preferences (10%).',
                icon: Cpu,
              },
              {
                step: '04',
                title: 'Skill Gap & Direct Apply',
                desc: 'See which skills you are missing for higher tier roles, and apply directly to the verified employer link.',
                icon: ShieldCheck,
              },
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  className="p-6 rounded-2xl glass-panel relative flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-xs font-mono font-bold text-indigo-400">
                        {item.step}
                      </span>
                      <div className="w-9 h-9 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
                        <Icon className="w-5 h-5" />
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                    <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>
      )}

      {/* ── WEEK-2 DEMO: Highlights Section — hidden ──────────────────── */}
      {false && (
      <section className="py-20 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-6">
                  <Brain className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Semantic MiniLM Vectors</h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Goes beyond keyword counting. Semantic representations capture contextual job
                  responsibilities to match candidates who have equivalent transferable experience.
                </p>
              </div>
            </div>

            <div className="p-8 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-400 flex items-center justify-center mb-6">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Targeted Skill Gap Roadmaps</h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Understand why a job didn't hit 90%+. View exact missing libraries or cloud
                  certifications and receive curated learning recommendations.
                </p>
              </div>
            </div>

            <div className="p-8 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-6">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Zero Spam or Scams</h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Multi-tier deduplication collapses identical postings across boards. You are always
                  redirected directly to the authentic original application portal.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
      )}

      {/* ── WEEK-2 DEMO: Footer — hidden ────────────────────────────── */}
      {false && (
      <footer className="mt-auto py-8 border-t border-slate-900 bg-slate-950 text-center text-xs text-slate-500">
        <p>JobPilot AI — Unified AI Job Discovery & Application Assistant.</p>
        <p className="mt-1">Powered by FastAPI, PyTorch, sentence-transformers, React, and PostgreSQL.</p>
      </footer>
      )}
    </div>
  );
};
