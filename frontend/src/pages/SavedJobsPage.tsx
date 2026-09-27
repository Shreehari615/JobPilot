import React, { useEffect, useState } from 'react';
import { Bookmark, ExternalLink, RefreshCw, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import { SavedJob } from '../types';

export const SavedJobsPage: React.FC = () => {
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchSavedJobs = async () => {
    setLoading(true);
    try {
      const data = await api.getSavedJobs();
      setSavedJobs(data);
    } catch (err) {
      console.error('Failed to load saved jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSavedJobs();
  }, []);

  const handleUnsave = async (jobId: number) => {
    try {
      await api.unsaveJob(jobId);
      setSavedJobs((prev) => prev.filter((s) => s.job_id !== jobId));
    } catch (err) {
      console.error('Failed to unsave job:', err);
    }
  };

  const handleStatusChange = async (jobId: number, newStatus: string) => {
    try {
      await api.saveJob(jobId, newStatus);
      setSavedJobs((prev) =>
        prev.map((s) => (s.job_id === jobId ? { ...s, status: newStatus } : s))
      );
    } catch (err) {
      console.error('Failed to update job status:', err);
    }
  };

  const filtered =
    filterStatus === 'all'
      ? savedJobs
      : savedJobs.filter((s) => s.status.toLowerCase() === filterStatus.toLowerCase());

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <Bookmark className="w-6 h-6 text-indigo-400" />
            Saved Jobs & Application Pipeline
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Track bookmarks, update submission status, and jump directly to the employer application.
          </p>
        </div>

        {/* Status Filter tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800">
          {['all', 'saved', 'applied'].map((tab) => (
            <button
              key={tab}
              onClick={() => setFilterStatus(tab)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                filterStatus === tab
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="p-16 text-center">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-2" />
          <p className="text-xs text-slate-400">Loading saved jobs...</p>
        </div>
      ) : filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="p-5 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition hover:border-slate-700"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300">
                    {item.job.work_mode || 'onsite'}
                  </span>
                  <span className="text-xs text-slate-400">
                    Saved on {new Date(item.saved_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white truncate">{item.job.title}</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {item.job.company} • {item.job.location || 'Remote'}
                </p>
              </div>

              <div className="flex items-center gap-3">
                {/* Status selector */}
                <select
                  value={item.status}
                  onChange={(e) => handleStatusChange(item.job_id, e.target.value)}
                  className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="saved">Bookmarked</option>
                  <option value="applied">Applied</option>
                  <option value="interviewing">Interviewing</option>
                  <option value="not_interested">Dismissed</option>
                </select>

                <a
                  href={item.job.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition"
                >
                  <span>Apply</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>

                <button
                  onClick={() => handleUnsave(item.job_id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-900 transition"
                  title="Remove"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl glass-panel border border-slate-800">
          <Bookmark className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No saved jobs found</h3>
          <p className="text-xs text-slate-400 mt-1">
            Explore active jobs or recommendations and bookmark roles you are interested in.
          </p>
        </div>
      )}
    </div>
  );
};
