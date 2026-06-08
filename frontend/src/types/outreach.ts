export interface OutreachContact {
  id: string
  job_id: string
  name: string | null
  title: string | null
  email: string | null
  linkedin_url: string | null
  source: string | null
  email_sent: boolean
  email_sent_at: string | null
  email_subject: string | null
  email_body: string | null
  created_at: string
}
