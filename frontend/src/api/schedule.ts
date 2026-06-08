import client from './client'

export interface SchedulePayload {
  profile_id: string
  cron_expression: string
  portals: string[]
}

export const getSchedules = () => client.get('/schedule').then((r) => r.data)

export const createSchedule = (data: SchedulePayload) =>
  client.post('/schedule', data).then((r) => r.data)

export const updateSchedule = (id: string, data: Partial<SchedulePayload> & { is_active?: boolean }) =>
  client.patch(`/schedule/${id}`, data).then((r) => r.data)

export const deleteSchedule = (id: string): Promise<void> =>
  client.delete(`/schedule/${id}`).then(() => undefined)
