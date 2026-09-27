import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  Copy,
  Database,
  Layers,
  Play,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';

export const AdminPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [duplicates, setDuplicates] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [collecting, setCollecting] = useState<boolean>(false);
  const [collectionResult, setCollectionResult] = useState<any>(null);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [st, src, dups] = await Promise.all([
        api.getAdminStats(),
        api.getJobSources(),
        api.getDuplicates(),
      ]);
      setStats(st);
      setSources(src);
      setDuplicates(dups);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleTriggerCollection = async () => {
    setCollecting(true);
    setCollectionResult(null);
    try {
      const res = await api.triggerCollection(50);
      setCollectionResult(res);
      await loadAdminData();
    } catch (err: any) {
      console.error('Collection trigger error:', err);
    } finally {
      setCollecting(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 bg-gradient-to-r from-purple-950/30 via-slate-900 to-indigo-950/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-2">
            <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />
            <span>Platform Administration & Ingestion Control</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">
            Job Ingestion & System Monitoring
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Orchestrate public APIs, compliance scrapers, deduplication filters, and semantic vector models.
          </p>
        </div>

        <button
          onClick={handleTriggerCollection}
          disabled={collecting}
          className="flex items-center gap-2 px-5 py-3 rounded-xl gradient-bg font-bold text-sm text-white shadow-lg shadow-indigo-600/30 hover:opacity-95 transition"
        >
          <Play className={`w-4 h-4 ${collecting ? 'animate-spin' : ''}`} />
          <span>{collecting ? 'Running Ingestion...' : 'Trigger Harvest Run'}</span>
        </button>
      </div>

      {collectionResult && (
        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{collectionResult.message}</span>
          </div>
          <div className="font-mono text-[11px] text-slate-300">
            Collected: {collectionResult.stats?.collected || 0} | Stored:{' '}
            {collectionResult.stats?.stored || 0} | Duplicates:{' '}
            {collectionResult.stats?.duplicates || 0}
          </div>
        </div>
      )}

      {/* Admin Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: 'Total Jobs', val: stats?.total_jobs ?? 0 },
          { label: 'Active Jobs', val: stats?.active_jobs ?? 0 },
          { label: 'Seed Jobs', val: stats?.seed_jobs ?? 0 },
          { label: 'Total Users', val: stats?.total_users ?? 0 },
          { label: 'Recommendations', val: stats?.total_recommendations ?? 0 },
          { label: 'Dup Clusters', val: stats?.duplicate_groups ?? 0 },
        ].map((item, idx) => (
          <div key={idx} className="p-4 rounded-2xl glass-panel border border-slate-800 text-center">
            <div className="text-xl font-extrabold text-white">{item.val}</div>
            <div className="text-[11px] text-slate-400 mt-1">{item.label}</div>
          </div>
        ))}
      </div>

      {/* Source Adapters Table */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-400" />
          Harvesting Source Adapters
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 uppercase border-b border-slate-800 bg-slate-900/40">
              <tr>
                <th className="py-3 px-4">Source Name</th>
                <th className="py-3 px-4">Adapter Type</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Jobs Ingested</th>
                <th className="py-3 px-4">Last Collected</th>
                <th className="py-3 px-4">Error Count</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {sources.map((src) => (
                <tr key={src.id} className="hover:bg-slate-900/40">
                  <td className="py-3 px-4 font-semibold text-white capitalize">{src.name}</td>
                  <td className="py-3 px-4 font-mono text-indigo-300">{src.source_type}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-emerald-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      Active
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono">{src.jobs_collected || 0}</td>
                  <td className="py-3 px-4 text-slate-400">
                    {src.last_collected_at
                      ? new Date(src.last_collected_at).toLocaleString()
                      : 'Never'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">{src.error_count || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3-Level Duplicate Detection Log */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Copy className="w-5 h-5 text-indigo-400" />
            3-Level Deduplication Log
          </h2>
          <span className="text-xs text-slate-400">Level 1: Exact | Level 2: Key | Level 3: Semantic</span>
        </div>

        {duplicates.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 uppercase border-b border-slate-800 bg-slate-900/40">
                <tr>
                  <th className="py-3 px-4">Primary Listing</th>
                  <th className="py-3 px-4">Duplicate Identified</th>
                  <th className="py-3 px-4">Level</th>
                  <th className="py-3 px-4">Similarity Score</th>
                  <th className="py-3 px-4">Detected At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {duplicates.map((dup) => (
                  <tr key={dup.id} className="hover:bg-slate-900/40">
                    <td className="py-3 px-4 font-medium text-white">
                      {dup.primary_job?.title || `Job #${dup.primary_job_id}`}
                      <span className="text-slate-500 block text-[11px]">
                        {dup.primary_job?.company}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {dup.duplicate_job?.title || `Job #${dup.duplicate_job_id}`}
                      <span className="text-slate-500 block text-[11px]">
                        {dup.duplicate_job?.company}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-indigo-300">Level {dup.detection_level}</td>
                    <td className="py-3 px-4 font-mono text-emerald-400">
                      {dup.similarity_score ? `${(dup.similarity_score * 100).toFixed(1)}%` : 'Exact 100%'}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {new Date(dup.detected_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-slate-500">No duplicate clusters identified yet.</p>
        )}
      </div>
    </div>
  );
};
