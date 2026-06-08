import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, RefreshCw, Briefcase, TrendingUp, Star, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { getJobs } from '../api/jobs'
import { scrapeNow, getScrapeStatus } from '../api/scrape'
import { createApplication, updateApplication, getApplications } from '../api/applications'
import JobCard from '../components/JobCard'
import StatusDropdown from '../components/StatusDropdown'
import type { Application } from '../types/application'

const PORTALS = ['linkedin', 'indeed', 'naukri', 'internshala', 'glassdoor', 'remotive', 'remoteok', 'greenhouse', 'lever', 'jobicy']

export default function Dashboard() {
  const qc = useQueryClient()
  const [filters, setFilters] = useState({ score_min: '', location: '', source: '' })
  const [scraping, setScraping] = useState(false)

  const { data: jobsData, isLoading } = useQuery({
    queryKey: ['jobs', filters],
    queryFn: () =>
      getJobs({
        score_min: filters.score_min ? Number(filters.score_min) : undefined,
        location: filters.location || undefined,
        source: filters.source || undefined,
      }),
  })

  const { data: applications } = useQuery({
    queryKey: ['applications'],
    queryFn: getApplications,
  })

  const appByJob = (applications ?? []).reduce<Record<string, Application>>(
    (acc, a) => ({ ...acc, [a.job_id]: a }),
    {},
  )

  const jobs = jobsData?.items ?? []
  const total = jobsData?.total ?? 0
  const highMatch = jobs.filter((j) => (j.match_score ?? 0) >= 80).length
  const applied = Object.values(appByJob).filter((a) => a.status === 'applied').length

  const { mutateAsync: triggerScrape } = useMutation({
    mutationFn: () => scrapeNow(),
    onSuccess: async ({ task_id }) => {
      setScraping(true)
      toast('Scraping started — this takes a few minutes…', { icon: '🔍' })
      await pollUntilDone(task_id)
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: changeStatus } = useMutation({
    mutationFn: async ({ jobId, status }: { jobId: string; status: string }) => {
      const existing = appByJob[jobId]
      if (existing) return updateApplication(existing.id, { status })
      const profile = await import('../api/profile').then((m) => m.getProfile())
      return createApplication({ job_id: jobId, profile_id: profile.id, status })
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
    onError: (e: Error) => toast.error(e.message),
  })

  async function pollUntilDone(id: string) {
    for (let i = 0; i < 120; i++) {
      await new Promise((r) => setTimeout(r, 3000))
      const s = await getScrapeStatus(id)
      if (s.state === 'SUCCESS') {
        toast.success(`Done — ${s.result?.jobs_new ?? 0} new jobs added`)
        qc.invalidateQueries({ queryKey: ['jobs'] })
        setScraping(false)
        return
      }
      if (s.state === 'FAILURE') {
        toast.error('Scrape failed: ' + (s.error ?? 'unknown error'))
        setScraping(false)
        return
      }
    }
    toast.error('Scrape timed out after 6 minutes')
    setScraping(false)
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Your personal job market, filtered for you.</p>
        </div>
        <button
          onClick={() => triggerScrape()}
          disabled={scraping}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white text-sm font-semibold rounded-xl shadow-sm transition-colors"
        >
          {scraping ? (
            <><Loader2 size={15} className="animate-spin" /> Scraping…</>
          ) : (
            <><RefreshCw size={15} /> Scrape Now</>
          )}
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-indigo-50 rounded-xl flex items-center justify-center">
              <Briefcase size={17} className="text-indigo-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Total Jobs</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{total}</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-green-50 rounded-xl flex items-center justify-center">
              <Star size={17} className="text-green-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Strong Match</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{highMatch}</p>
          <p className="text-xs text-gray-400 mt-1">score ≥ 80</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-blue-50 rounded-xl flex items-center justify-center">
              <TrendingUp size={17} className="text-blue-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Applied</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{applied}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap items-center">
        <span className="text-sm font-medium text-gray-500">Filter:</span>
        <input
          type="number"
          placeholder="Min score"
          value={filters.score_min}
          onChange={(e) => setFilters((f) => ({ ...f, score_min: e.target.value }))}
          className="w-28 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
        />
        <input
          placeholder="Location"
          value={filters.location}
          onChange={(e) => setFilters((f) => ({ ...f, location: e.target.value }))}
          className="w-40 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
        />
        <select
          value={filters.source}
          onChange={(e) => setFilters((f) => ({ ...f, source: e.target.value }))}
          className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
        >
          <option value="">All portals</option>
          {PORTALS.map((p) => (
            <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
          ))}
        </select>
        {(filters.score_min || filters.location || filters.source) && (
          <button
            onClick={() => setFilters({ score_min: '', location: '', source: '' })}
            className="text-xs text-indigo-600 hover:underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Job list */}
      {isLoading ? (
        <div className="flex justify-center py-24">
          <Loader2 size={28} className="animate-spin text-indigo-600" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-24 bg-white rounded-2xl border border-dashed border-gray-200">
          <Clock size={36} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">No jobs yet</p>
          <p className="text-sm text-gray-400 mt-1">Set up your profile then click Scrape Now</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              statusEl={
                <StatusDropdown
                  status={appByJob[job.id]?.status ?? 'saved'}
                  onChange={(status) => changeStatus({ jobId: job.id, status })}
                />
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}
