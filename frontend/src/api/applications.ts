import client from './client'
import type { Application } from '../types/application'

export const getApplications = (): Promise<Application[]> =>
  client.get('/applications').then((r) => r.data)

export const createApplication = (data: {
  job_id: string
  profile_id: string
  status?: string
}): Promise<Application> => client.post('/applications', data).then((r) => r.data)

export const updateApplication = (
  id: string,
  data: {
    status?: string
    notes?: string
    outcome?: string | null
    interview_date?: string | null
    outcome_date?: string | null
    feedback?: string | null
  },
): Promise<Application> => client.patch(`/applications/${id}`, data).then((r) => r.data)
