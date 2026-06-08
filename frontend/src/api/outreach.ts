import client from './client'
import type { OutreachContact } from '../types/outreach'

export const findContacts = (job_id: string): Promise<OutreachContact[]> =>
  client.post('/outreach/find-contacts', null, { params: { job_id } }).then((r) => r.data)

export const getContacts = (job_id: string): Promise<OutreachContact[]> =>
  client.get(`/outreach/${job_id}`).then((r) => r.data)

export const sendEmail = (
  contact_id: string,
  data: { subject: string; body: string },
): Promise<OutreachContact> =>
  client.post(`/outreach/${contact_id}/send`, data).then((r) => r.data)
