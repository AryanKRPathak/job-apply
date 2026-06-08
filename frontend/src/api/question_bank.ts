import client from './client'
import type { QuestionBank } from '../types/question_bank'

export const getQuestions = (profileId: string): Promise<QuestionBank[]> =>
  client.get(`/question-bank/${profileId}`).then((r) => r.data)

export const createQuestion = (data: {
  profile_id: string
  question: string
  answer?: string | null
  category?: string | null
}): Promise<QuestionBank> => client.post('/question-bank', data).then((r) => r.data)

export const updateQuestion = (
  id: string,
  data: { question?: string; answer?: string | null; category?: string | null },
): Promise<QuestionBank> => client.patch(`/question-bank/${id}`, data).then((r) => r.data)

export const deleteQuestion = (id: string): Promise<void> =>
  client.delete(`/question-bank/${id}`).then(() => undefined)
