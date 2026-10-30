export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface Profile {
  id?: number;
  user_id?: number;
  full_name?: string;
  phone?: string;
  location?: string;
  bio?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  experience_years?: number;
  experience_level?: string;
  expected_salary_min?: number;
  expected_salary_max?: number;
}

export interface UserPreferences {
  id?: number;
  user_id?: number;
  preferred_roles: string[];
  preferred_locations: string[];
  remote_preference: string;
  employment_type: string;
  min_salary?: number;
  max_salary?: number;
}

export interface JobSkill {
  skill_name: string;
  is_required: boolean;
}

export interface Job {
  id: number;
  external_id?: string;
  title: string;
  company?: string;
  location?: string;
  description?: string;
  responsibilities?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  job_type?: string;
  work_mode?: string;
  experience_min?: number;
  experience_max?: number;
  education_required?: string;
  original_url: string;
  posted_date?: string;
  collected_at?: string;
  is_seed_data: boolean;
  source_name?: string;
  skills: JobSkill[];
}

export interface ScoreBreakdown {
  skill_match: string;
  semantic_similarity: string;
  experience_match: string;
  education_match: string;
  preference_match: string;
}

export interface Explanation {
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  reasons: string[];
  score_breakdown: ScoreBreakdown;
  weights_used?: Record<string, number>;
}

export interface Recommendation {
  id: number;
  job_id: number;
  overall_score: number;
  skill_score: number;
  semantic_score: number;
  experience_score: number;
  education_score: number;
  preference_score: number;
  explanation?: Explanation;
  computed_at: string;
  job: Job;
}

export interface SkillGapItem {
  skill_name: string;
  gap_type: 'matching' | 'partial' | 'missing';
}

export interface RecommendationDetail extends Recommendation {
  skill_gaps: SkillGapItem[];
}

export interface SavedJob {
  id: number;
  job_id: number;
  status: string;
  notes?: string;
  saved_at: string;
  job: Job;
}

export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  file_type: string;
  file_size_bytes?: number;
  status: string;
  processed_at?: string;
  created_at: string;
}

export interface ResumeProject {
  title: string;
  description?: string;
  highlights?: string[];
  skills?: string[];
}

export interface ResumeEducation {
  degree?: string;
  institution?: string;
  year?: string | number;
  graduation_year?: number;
  grade?: string;
  field_of_study?: string;
}

export interface ResumeAnalysis {
  resume_id: number;
  name?: string;
  email?: string;
  phone?: string;
  skills: string[];
  education: ResumeEducation[];
  experience: Array<{ title?: string; company?: string; duration?: string; job_title?: string; start?: string; end?: string; description?: string }>;
  total_experience_years: number;
  job_titles: string[];
  certifications: string[];
  projects: Array<string | ResumeProject>;
  summary?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
