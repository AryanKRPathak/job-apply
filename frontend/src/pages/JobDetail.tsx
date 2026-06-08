import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, ExternalLink, MapPin, Building2, ChevronDown } from 'lucide-react'
import { getJob } from '../api/jobs'
import CoverLetterEditor from '../components/CoverLetterEditor'
import ScoreIndicator from '../components/ScoreIndicator'

export default function JobDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: job, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => getJob(id!),
    enabled: !!id,
  })

  if (isLoading)
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">Loading…</div>
    )
  if (!job)
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">Job not found</div>
    )

  return (
    <div className="max-w-3xl mx-auto">
      <Link
        to="/dashboard"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 mb-6 transition-colors"
      >
        <ArrowLeft size={14} /> Back to Dashboard
      </Link>

      {/* Job header card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-5">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 text-sm text-gray-600 font-medium">
                <Building2 size={14} className="text-gray-400" />
                {job.company}
              </span>
              {job.location && (
                <span className="inline-flex items-center gap-1 text-sm text-gray-400">
                  <MapPin size={13} /> {job.location}
                </span>
              )}
              {job.is_remote && (
                <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-0.5 rounded-full font-medium">
                  Remote
                </span>
              )}
            </div>
          </div>
          <ScoreIndicator score={job.match_score} />
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          {job.salary_range && (
            <span className="text-sm text-gray-500 bg-gray-50 border border-gray-200 px-3 py-1 rounded-full">
              💰 {job.salary_range}
            </span>
          )}
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 px-3 py-1 rounded-full transition-colors"
          >
            <ExternalLink size={13} /> Open listing
          </a>
        </div>

        {/* AI reasoning */}
        {job.score_reasoning && (
          <div className="mt-5 p-4 bg-indigo-50 border border-indigo-100 rounded-xl">
            <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wider mb-1.5">
              Why this score?
            </p>
            <p className="text-sm text-indigo-900 leading-relaxed">{job.score_reasoning}</p>
          </div>
        )}

        {/* Job description collapsible */}
        {job.description && (
          <details className="mt-5 group">
            <summary className="flex items-center gap-1.5 text-sm font-semibold text-gray-700 cursor-pointer list-none hover:text-gray-900">
              <ChevronDown size={14} className="transition-transform group-open:rotate-180" />
              Job description
            </summary>
            <div className="mt-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
              <pre className="text-sm text-gray-600 whitespace-pre-wrap font-sans leading-relaxed">
                {job.description}
              </pre>
            </div>
          </details>
        )}
      </div>

      {/* Cover letter editor */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <h2 className="text-base font-semibold text-gray-900 mb-4">Cover Letter</h2>
        <CoverLetterEditor jobId={job.id} initial={job.cover_letter} />
      </div>
    </div>
  )
}
