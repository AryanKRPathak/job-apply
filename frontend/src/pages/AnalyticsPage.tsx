import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { TrendingUp, CheckCircle2, XCircle, Clock, MessageSquare, Award } from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'
import { getApplications, updateApplication } from '../api/applications'
import { getJobs } from '../api/jobs'
import type { Application } from '../types/application'

const OUTCOMES = [
  { value: 'interview', label: 'Interview', color: 'bg-blue-100 text-blue-700 border-blue-200' },
  { value: 'offer', label: 'Offer', color: 'bg-green-100 text-green-700 border-green-200' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-700 border-red-200' },
  { value: 'ghosted', label: 'Ghosted', color: 'bg-gray-100 text-gray-600 border-gray-200' },
]

function OutcomeSelect({ app }: { app: Application }) {
  const qc = useQueryClient()
  const [open, setOpen] = useState(false)
  const { mutate } = useMutation({
    mutationFn: (outcome: string) => updateApplication(app.id, { outcome }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
    onError: (e: Error) => toast.error(e.message),
  })

  const current = OUTCOMES.find((o) => o.value === app.outcome)

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className={`text-xs border px-2.5 py-1 rounded-full font-medium transition-colors ${
          current ? current.color : 'bg-gray-50 text-gray-500 border-gray-200 hover:border-indigo-300'
        }`}
      >
        {current ? current.label : 'Set outcome'}
      </button>
      {open && (
        <div className="absolute right-0 top-8 z-10 bg-white border border-gray-200 rounded-xl shadow-lg p-1.5 min-w-[130px]">
          {OUTCOMES.map((o) => (
            <button
              key={o.value}
              onClick={() => { mutate(o.value); setOpen(false) }}
              className="w-full text-left px-3 py-1.5 text-xs rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              {o.label}
            </button>
          ))}
          {app.outcome && (
            <button
              onClick={() => { mutate(''); setOpen(false) }}
              className="w-full text-left px-3 py-1.5 text-xs rounded-lg hover:bg-red-50 text-red-500 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default function AnalyticsPage() {
  const { data: applications = [], isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: getApplications,
  })

  const { data: jobsData } = useQuery({
    queryKey: ['jobs', {}],
    queryFn: () => getJobs({}),
  })

  const jobs = jobsData?.items ?? []
  const jobMap = Object.fromEntries(jobs.map((j) => [j.id, j]))

  const applied = applications.filter((a) => a.status === 'applied')
  const interviews = applications.filter((a) => a.outcome === 'interview' || a.outcome === 'offer')
  const offers = applications.filter((a) => a.outcome === 'offer')
  const rejected = applications.filter((a) => a.outcome === 'rejected')

  const responseRate = applied.length > 0
    ? Math.round(((interviews.length + rejected.length) / applied.length) * 100)
    : 0
  const interviewRate = applied.length > 0
    ? Math.round((interviews.length / applied.length) * 100)
    : 0

  const recentApplied = [...applied]
    .sort((a, b) => new Date(b.applied_at ?? b.created_at).getTime() - new Date(a.applied_at ?? a.created_at).getTime())
    .slice(0, 20)

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-500 mt-1">Track your application outcomes and response rates.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="w-9 h-9 bg-indigo-50 rounded-xl flex items-center justify-center mb-3">
            <TrendingUp size={17} className="text-indigo-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{applied.length}</p>
          <p className="text-xs text-gray-500 mt-1">Applied</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="w-9 h-9 bg-blue-50 rounded-xl flex items-center justify-center mb-3">
            <MessageSquare size={17} className="text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{interviews.length}</p>
          <p className="text-xs text-gray-500 mt-1">Interviews</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="w-9 h-9 bg-green-50 rounded-xl flex items-center justify-center mb-3">
            <Award size={17} className="text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{offers.length}</p>
          <p className="text-xs text-gray-500 mt-1">Offers</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="w-9 h-9 bg-amber-50 rounded-xl flex items-center justify-center mb-3">
            <CheckCircle2 size={17} className="text-amber-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{interviewRate}%</p>
          <p className="text-xs text-gray-500 mt-1">Interview rate</p>
        </div>
      </div>

      {/* Funnel */}
      {applied.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-8">
          <h2 className="text-sm font-semibold text-gray-800 mb-5">Application funnel</h2>
          <div className="flex flex-col gap-3">
            {[
              { label: 'Applied', count: applied.length, color: 'bg-indigo-500', pct: 100 },
              { label: 'Response received', count: interviews.length + rejected.length, color: 'bg-blue-500', pct: responseRate },
              { label: 'Interview', count: interviews.length, color: 'bg-teal-500', pct: interviewRate },
              { label: 'Offer', count: offers.length, color: 'bg-green-500', pct: applied.length > 0 ? Math.round((offers.length / applied.length) * 100) : 0 },
            ].map(({ label, count, color, pct }) => (
              <div key={label} className="flex items-center gap-4">
                <span className="text-xs text-gray-500 w-36 shrink-0">{label}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2">
                  <div
                    className={`${color} h-2 rounded-full transition-all`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="text-xs font-semibold text-gray-700 w-16 text-right">
                  {count} <span className="text-gray-400 font-normal">({pct}%)</span>
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Applications tracker */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-gray-800">Application tracker</h2>
          <p className="text-xs text-gray-400 mt-0.5">Set outcome for each application to track your funnel.</p>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-gray-400 text-sm">Loading…</div>
        ) : recentApplied.length === 0 ? (
          <div className="p-12 text-center">
            <Clock size={32} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 text-sm">No applications yet.</p>
            <p className="text-xs text-gray-400 mt-1">Mark jobs as "Applied" on the Dashboard to track them here.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {recentApplied.map((app) => {
              const job = jobMap[app.job_id]
              return (
                <div key={app.id} className="flex items-center gap-4 px-6 py-3.5 hover:bg-gray-50 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {job?.title ?? 'Unknown role'}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {job?.company ?? '—'}
                      {app.applied_at && (
                        <span className="ml-2 text-gray-400">
                          Applied {new Date(app.applied_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                        </span>
                      )}
                    </p>
                  </div>
                  {app.outcome === 'rejected' && (
                    <XCircle size={14} className="text-red-400 shrink-0" />
                  )}
                  {app.outcome === 'offer' && (
                    <Award size={14} className="text-green-500 shrink-0" />
                  )}
                  <OutcomeSelect app={app} />
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
