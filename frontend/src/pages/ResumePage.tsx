import React, { useEffect, useRef, useState } from 'react';
import {
  AlertCircle,
  Briefcase,
  CheckCircle2,
  Clock,
  Code2,
  FileCheck,
  FileText,
  GraduationCap,
  Sparkles,
  UploadCloud,
  User,
} from 'lucide-react';
import { api } from '../api/client';
import { SkillTag } from '../components/SkillTag';
import { Resume, ResumeAnalysis } from '../types';

export const ResumePage: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadResumesAndAnalysis = async () => {
    setLoading(true);
    try {
      const list = await api.getResumes();
      setResumes(list);

      if (list.length > 0) {
        // Load latest analysis
        const latest = await api.getLatestAnalysis().catch(() => null);
        if (latest) {
          setAnalysis(latest);
        } else {
          // If no latest cached, fetch by resume id
          const first = await api.getResumeAnalysis(list[0].id).catch(() => null);
          if (first) setAnalysis(first);
        }
      }
    } catch (err) {
      console.error('Error loading resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResumesAndAnalysis();
  }, []);

  const handleFileUpload = async (file: File) => {
    setError(null);

    // Validate type
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setError('Only PDF and DOCX formats are supported.');
      return;
    }

    // Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be under 10MB.');
      return;
    }

    setUploading(true);
    try {
      const resume = await api.uploadResume(file);
      // Refresh analysis
      await loadResumesAndAnalysis();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to upload and analyze resume. Please try again.'
      );
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl glass-panel border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            Intelligent Document Parsing
          </span>
        </div>
        <h1 className="text-2xl font-extrabold text-white">Resume & NLP Skill Extractor</h1>
        <p className="text-xs text-slate-400 mt-1 max-w-2xl">
          Upload your resume in PDF or DOCX format. Our spaCy and NLTK pipeline automatically parses
          your contact info, education, years of experience, and canonicalizes your technical skills.
        </p>
      </div>

      {/* Upload Box */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`p-10 rounded-3xl border-2 border-dashed transition-all cursor-pointer text-center ${
          dragOver
            ? 'border-indigo-500 bg-indigo-950/30'
            : 'border-slate-700/80 hover:border-slate-500 bg-slate-900/40'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileUpload(e.target.files[0]);
            }
          }}
        />

        <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 text-indigo-400 mx-auto flex items-center justify-center mb-4 shadow-lg shadow-indigo-600/10">
          <UploadCloud className={`w-8 h-8 ${uploading ? 'animate-bounce' : ''}`} />
        </div>

        <h3 className="text-base font-bold text-white mb-1">
          {uploading ? 'Analyzing document with NLP pipeline...' : 'Click to browse or drag & drop'}
        </h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto">
          Supported formats: <strong className="text-slate-200">PDF, DOCX</strong> (Up to 10MB)
        </p>

        {uploading && (
          <div className="mt-4 flex items-center justify-center gap-2 text-xs text-indigo-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
            <span>Extracting skills, entities, and generating MiniLM vectors...</span>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* NLP Extraction Results */}
      {analysis && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-emerald-400" />
              Verified Extraction Results
            </h2>
            <span className="text-xs text-slate-400">
              Extracted from{' '}
              <strong className="text-slate-200">
                {resumes[0]?.filename || 'Uploaded Resume'}
              </strong>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Candidate Summary Card */}
            <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
                <User className="w-4 h-4" />
                Contact & Profile
              </h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-xs text-slate-500 block">Extracted Name</span>
                  <span className="font-semibold text-white">
                    {analysis.name || 'Not detected in header'}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Email Address</span>
                  <span className="text-slate-300">{analysis.email || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Phone</span>
                  <span className="text-slate-300">{analysis.phone || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Detected Experience</span>
                  <span className="font-semibold text-emerald-400">
                    {analysis.total_experience_years.toFixed(1)} Years
                  </span>
                </div>
              </div>
            </div>

            {/* Extracted Skills Card */}
            <div className="md:col-span-2 p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
                  <Code2 className="w-4 h-4" />
                  Canonical Technical Skills ({analysis.skills?.length || 0})
                </h3>
                <span className="text-xs font-mono text-emerald-400">Taxonomy Normalized</span>
              </div>

              <div className="flex flex-wrap gap-2 max-h-56 overflow-y-auto pr-2">
                {analysis.skills && analysis.skills.length > 0 ? (
                  analysis.skills.map((skill, idx) => (
                    <SkillTag key={idx} name={skill} status="matching" size="md" />
                  ))
                ) : (
                  <span className="text-xs text-slate-500">No skills recognized in text.</span>
                )}
              </div>
            </div>
          </div>

          {/* Experience & Education */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Experience */}
            <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
                <Briefcase className="w-4 h-4" />
                Work History & Projects
              </h3>
              {analysis.experience && analysis.experience.length > 0 ? (
                <div className="space-y-3">
                  {analysis.experience.map((exp, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs"
                    >
                      <div className="font-bold text-white text-sm">{exp.title || 'Role'}</div>
                      <div className="text-slate-400">{exp.company || 'Company'}</div>
                      {exp.duration && <div className="text-slate-500 mt-1">{exp.duration}</div>}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No structured roles identified in text.</p>
              )}
            </div>

            {/* Education */}
            <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
                <GraduationCap className="w-4 h-4" />
                Education Credentials
              </h3>
              {analysis.education && analysis.education.length > 0 ? (
                <div className="space-y-3">
                  {analysis.education.map((edu, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs"
                    >
                      <div className="font-bold text-white text-sm">
                        {edu.degree || 'Degree'}
                      </div>
                      <div className="text-slate-400">{edu.institution || 'University'}</div>
                      {edu.year && (
                        <div className="text-slate-500 mt-1">Graduation: {edu.year}</div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No education entries extracted.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
