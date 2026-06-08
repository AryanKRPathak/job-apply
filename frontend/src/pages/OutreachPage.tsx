import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Loader2, Mail, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import { getJob } from '../api/jobs'
import { findContacts, getContacts, sendEmail } from '../api/outreach'
import type { OutreachContact } from '../types/outreach'

export default function OutreachPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const qc = useQueryClient()
  const [emailDraft, setEmailDraft] = useState<{ contactId: string; subject: string; body: string } | null>(null)

  const { data: job } = useQuery({ queryKey: ['job', jobId], queryFn: () => getJob(jobId!), enabled: !!jobId })
  const { data: contacts, isLoading } = useQuery({
    queryKey: ['outreach', jobId],
    queryFn: () => getContacts(jobId!),
    enabled: !!jobId,
  })

  const { mutate: search, isPending: searching } = useMutation({
    mutationFn: () => findContacts(jobId!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['outreach', jobId] })
      toast.success('Contacts found')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: send, isPending: sending } = useMutation({
    mutationFn: ({ contactId, subject, body }: { contactId: string; subject: string; body: string }) =>
      sendEmail(contactId, { subject, body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['outreach', jobId] })
      setEmailDraft(null)
      toast.success('Email sent')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  function openDraft(c: OutreachContact) {
    setEmailDraft({
      contactId: c.id,
      subject: `Application for ${job?.title ?? 'the role'} at ${job?.company ?? 'your company'}`,
      body: job?.cover_letter ?? '',
    })
  }

  return (
    <div className="max-w-2xl">
      <Link to={`/jobs/${jobId}`} className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 mb-6">
        <ArrowLeft size={14} /> Back to job
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Outreach</h1>
          {job && <p className="text-sm text-gray-500">{job.title} · {job.company}</p>}
        </div>
        <button
          onClick={() => search()}
          disabled={searching}
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm rounded-lg disabled:opacity-60 transition-colors"
        >
          {searching ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
          Find contacts
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16"><Loader2 size={24} className="animate-spin text-brand-600" /></div>
      ) : (
        <div className="flex flex-col gap-3">
          {(contacts ?? []).length === 0 && (
            <p className="text-center text-gray-400 py-16">No contacts yet — click Find contacts.</p>
          )}
          {(contacts ?? []).map((c) => (
            <div key={c.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{c.name ?? c.email ?? 'Unknown'}</p>
                {c.title && <p className="text-xs text-gray-500">{c.title}</p>}
                {c.email && <p className="text-xs text-gray-400">{c.email}</p>}
                <span className="text-xs text-gray-400 capitalize">{c.source}</span>
              </div>
              {c.email_sent ? (
                <span className="text-xs text-green-600 font-medium">Sent</span>
              ) : (
                <button
                  onClick={() => openDraft(c)}
                  className="inline-flex items-center gap-1 text-xs text-brand-600 hover:underline"
                >
                  <Mail size={12} /> Draft email
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {emailDraft && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg p-6 flex flex-col gap-4">
            <h2 className="text-base font-semibold">Draft Email</h2>
            <input
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="Subject"
              value={emailDraft.subject}
              onChange={(e) => setEmailDraft((d) => d && { ...d, subject: e.target.value })}
            />
            <textarea
              className="w-full min-h-[200px] px-3 py-2 text-sm border border-gray-200 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-brand-500"
              value={emailDraft.body}
              onChange={(e) => setEmailDraft((d) => d && { ...d, body: e.target.value })}
            />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setEmailDraft(null)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Cancel</button>
              <button
                disabled={sending}
                onClick={() => send(emailDraft)}
                className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm rounded-lg disabled:opacity-60 transition-colors"
              >
                {sending ? 'Sending…' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
