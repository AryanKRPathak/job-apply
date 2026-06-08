export interface Application {
  id: string
  job_id: string
  profile_id: string
  status: 'saved' | 'applied' | 'interview' | 'rejected' | 'offer'
  applied_at: string | null
  cover_letter_used: string | null
  notes: string | null
  outcome: 'interview' | 'offer' | 'rejected' | 'ghosted' | null
  interview_date: string | null
  outcome_date: string | null
  feedback: string | null
  created_at: string
  updated_at: string | null
}
