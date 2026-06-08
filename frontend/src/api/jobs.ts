import client from './client'
import type { Job, JobListResponse } from '../types/job'

interface JobFilters {
  score_min?: number
  location?: string
  company?: string
  source?: string
  page?: number
  limit?: number
}

export const getJobs = (filters: JobFilters = {}): Promise<JobListResponse> =>
  client.get('/jobs', { params: filters }).then((r) => r.data)

export const getJob = (id: string): Promise<Job> =>
  client.get(`/jobs/${id}`).then((r) => r.data)

export const updateCoverLetter = (id: string, cover_letter: string): Promise<Job> =>
  client.patch(`/jobs/${id}/cover-letter`, { cover_letter }).then((r) => r.data)

export const deleteJob = (id: string): Promise<void> =>
  client.delete(`/jobs/${id}`).then(() => undefined)
