export interface Job {
  id: string
  external_id: string
  source: string
  title: string
  company: string
  location: string | null
  description: string | null
  url: string
  posted_date: string | null
  scraped_at: string
  match_score: number | null
  score_reasoning: string | null
  cover_letter: string | null
  is_remote: boolean
  salary_range: string | null
}

export interface JobListResponse {
  items: Job[]
  total: number
  page: number
  limit: number
}
