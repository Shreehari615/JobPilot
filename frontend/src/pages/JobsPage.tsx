import React, { useEffect, useState } from 'react';
import {
  Briefcase,
  ChevronLeft,
  ChevronRight,
  Filter,
  MapPin,
  RefreshCw,
  Search,
  SlidersHorizontal,
  X,
} from 'lucide-react';
import { api } from '../api/client';
import { JobCard } from '../components/JobCard';
import { Job, PaginatedResponse } from '../types';

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pages, setPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [syncing, setSyncing] = useState<boolean>(false);

  // Filter states
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobType, setJobType] = useState('');
  const [workMode, setWorkMode] = useState('');
  const [sortBy, setSortBy] = useState('posted_date');
  const [realOnly, setRealOnly] = useState<boolean>(true);
  const [showFilters, setShowFilters] = useState(false);

  const fetchJobs = async (pageNumber: number = 1) => {
    setLoading(true);
    try {
      const params: Record<string, any> = {
        page: pageNumber,
        page_size: 12,
        sort_by: sortBy,
      };
      if (query.trim()) params.query = query.trim();
      if (location) params.location = location;
      if (jobType) params.job_type = jobType;
      if (workMode) params.work_mode = workMode;
      if (realOnly) params.real_only = true;

      const res: PaginatedResponse<Job> = await api.getJobs(params);
      setJobs(res.items);
      setTotal(res.total);
      setPage(res.page);
      setPages(res.pages);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(1);
  }, [location, jobType, workMode, sortBy, realOnly]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(1);
  };

  const handleSyncJobs = async () => {
    setSyncing(true);
    try {
      await api.syncJobs(30);
      await fetchJobs(1);
    } catch (err) {
      console.error('Failed to sync live jobs:', err);
    } finally {
      setSyncing(false);
    }
  };

  const clearFilters = () => {
    setQuery('');
    setLocation('');
    setJobType('');
    setWorkMode('');
    setSortBy('posted_date');
    setRealOnly(true);
    fetchJobs(1);
  };

  const hasActiveFilters = !!(query || location || jobType || workMode || sortBy !== 'posted_date' || !realOnly);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with Search and Filter bar */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800">
        <div className="mb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
              <Briefcase className="w-6 h-6 text-indigo-400" />
              Explore Verified Real-Market Jobs
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Live, verified openings harvested in real time from Remotive, Arbeitnow, Jobicy, and active employers.
              Every link directs to the genuine company application page.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSyncJobs}
              disabled={syncing}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5 transition shadow-sm"
              title="Fetch fresh real-world jobs from live APIs"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
              <span>{syncing ? 'Syncing...' : 'Sync Live Jobs'}</span>
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by job title, company, or tech keywords (e.g. Python, React, Cloud, AI)..."
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          <div className="flex gap-2 items-center">
            <button
              type="submit"
              className="px-6 py-3 rounded-xl gradient-bg font-semibold text-sm text-white shadow-md shadow-indigo-600/20 hover:opacity-95 transition"
            >
              Search
            </button>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-3 rounded-xl border text-sm font-medium transition flex items-center gap-2 ${
                showFilters || hasActiveFilters
                  ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300'
                  : 'bg-slate-900 border-slate-700 text-slate-300 hover:text-white'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </form>

        {/* Filter controls expandable */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-4 gap-3 animate-fade-in">
            {/* Work Mode */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                Work Mode
              </label>
              <select
                value={workMode}
                onChange={(e) => setWorkMode(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Work Modes</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                Location
              </label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Locations</option>
                <option value="Bengaluru">Bengaluru</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Pune">Pune</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Delhi NCR">Delhi NCR</option>
                <option value="Chennai">Chennai</option>
                <option value="Remote">Remote</option>
              </select>
            </div>

            {/* Job Type */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                Employment Type
              </label>
              <select
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Types</option>
                <option value="full-time">Full-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
                <option value="part-time">Part-time</option>
              </select>
            </div>

            {/* Sort */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                Sort By
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="posted_date">Latest Posted</option>
                <option value="salary">Highest Salary</option>
              </select>
            </div>

            <div className="sm:col-span-4 flex items-center justify-between pt-2 border-t border-slate-800/60 mt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none text-xs text-slate-300 hover:text-white">
                <input
                  type="checkbox"
                  checked={realOnly}
                  onChange={(e) => setRealOnly(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <span className="font-semibold text-emerald-400">Real Market Jobs Only</span>
                <span className="text-slate-500 text-[11px]">(Hides demo/mock postings)</span>
              </label>

              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300 font-medium"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Reset All Filters</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Results Meta */}
      <div className="flex items-center justify-between px-1">
        <span className="text-xs text-slate-400 font-medium">
          Showing {jobs.length} of {total} jobs found
        </span>
        <span className="text-xs text-slate-500 font-mono">
          Page {page} of {pages || 1}
        </span>
      </div>

      {/* Jobs Grid */}
      {loading ? (
        <div className="p-16 text-center">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-2" />
          <p className="text-xs text-slate-400">Loading job postings...</p>
        </div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl glass-panel border border-slate-800">
          <Briefcase className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No jobs matched your query</h3>
          <p className="text-xs text-slate-400 mt-1 mb-4">
            Try adjusting your search criteria or clearing filters to see more results.
          </p>
          <button
            onClick={clearFilters}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Pagination Controls */}
      {pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <button
            onClick={() => fetchJobs(page - 1)}
            disabled={page <= 1}
            className="p-2 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="text-xs font-medium text-slate-400 px-3">
            Page {page} of {pages}
          </span>

          <button
            onClick={() => fetchJobs(page + 1)}
            disabled={page >= pages}
            className="p-2 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};
