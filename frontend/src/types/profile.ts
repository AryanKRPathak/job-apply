export interface Profile {
  id: string
  full_name: string
  email: string | null
  phone: string | null
  resume_text: string | null
  resume_filename: string | null
  target_titles: string[]
  target_locations: string[]
  skills: string[]
  years_exp: number | null
  story: string | null
  company_blacklist: string[]
  company_whitelist: string[]
  title_keyword_blacklist: string[]
  min_salary: number | null
  created_at: string
  updated_at: string
}

export interface ResumeUploadResponse {
  extracted_text: string
  detected_skills: string[]
  filename: string
  full_name: string
  email: string
  phone: string
  years_exp: number | null
  story: string
  suggested_titles: string[]
}
