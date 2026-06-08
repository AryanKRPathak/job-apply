import client from './client'
import type { Profile, ResumeUploadResponse } from '../types/profile'

export const getProfile = (): Promise<Profile> =>
  client.get('/profile').then((r) => r.data)

export const createOrUpdateProfile = (data: Partial<Profile>): Promise<Profile> =>
  client.post('/profile', data).then((r) => r.data)

export const patchProfile = (data: Partial<Profile>): Promise<Profile> =>
  client.patch('/profile', data).then((r) => r.data)

export const uploadResume = (file: File): Promise<ResumeUploadResponse> => {
  const form = new FormData()
  form.append('file', file)
  return client
    .post('/profile/upload-resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}
