import { Link } from 'react-router-dom'
import { ExternalLink, Mail, MapPin, Building2 } from 'lucide-react'
import type { Job } from '../types/job'
import ScoreIndicator from './ScoreIndicator'

interface Props {
  job: Job
  statusEl?: React.ReactNode
}

const sourceColors: Record<string, string> = {
  linkedin:     'bg-blue-50 text-blue-700 border-blue-100',
  indeed:       'bg-purple-50 text-purple-700 border-purple-100',
  naukri:       'bg-orange-50 text-orange-700 border-orange-100',
  glassdoor:    'bg-green-50 text-green-700 border-green-100',
  internshala:  'bg-yellow-50 text-yellow-700 border-yellow-100',
  jsearch:      'bg-gray-100 text-gray-600 border-gray-200',
  remotive:     'bg-violet-50 text-violet-700 border-violet-100',
  remoteok:     'bg-cyan-50 text-cyan-700 border-cyan-100',
  arbeitnow:    'bg-rose-50 text-rose-700 border-rose-100',
  jobicy:       'bg-teal-50 text-teal-700 border-teal-100',
  greenhouse:   'bg-emerald-50 text-emerald-700 border-emerald-100',
  lever:        'bg-pink-50 text-pink-700 border-pink-100',
}

export default function JobCard({ job, statusEl }: Props) {
  const sourcePill = sourceColors[job.source] ?? 'bg-gray-100 text-gray-600 border-gray-200'

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 hover:shadow-md hover:border-indigo-200 transition-all group">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Title */}
          <Link
            to={`/jobs/${job.id}`}
            className="text-base font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-1"
          >
            {job.title}
          </Link>

          {/* Company & Location row */}
          <div className="flex items-center gap-3 mt-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1 text-sm text-gray-600 font-medium">
              <Building2 size={13} className="text-gray-400" />
              {job.company}
            </span>
            {job.location && (
              <span className="inline-flex items-center gap-1 text-xs text-gray-400">
                <MapPin size={11} />
                {job.location}
              </span>
            )}
            {job.is_remote && (
              <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-0.5 rounded-full font-medium">
                Remote
              </span>
            )}
          </div>

          {/* Score reasoning preview */}
          {job.score_reasoning && (
            <p className="text-xs text-gray-400 mt-2 line-clamp-1">{job.score_reasoning}</p>
          )}
        </div>

        {/* Right side: score + status */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          <ScoreIndicator score={job.match_score} />
          {statusEl}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100">
        <span className={`text-xs border px-2 py-0.5 rounded-full font-medium capitalize ${sourcePill}`}>
          {job.source}
        </span>
        {job.salary_range && (
          <span className="text-xs text-gray-500">{job.salary_range}</span>
        )}
        <div className="ml-auto flex items-center gap-3">
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
          >
            <ExternalLink size={12} /> Apply
          </a>
          <Link
            to={`/outreach/${job.id}`}
            className="inline-flex items-center gap-1 text-xs text-gray-400 hover:text-gray-700 font-medium"
          >
            <Mail size={12} /> Contacts
          </Link>
          <Link
            to={`/jobs/${job.id}`}
            className="inline-flex items-center gap-1 text-xs text-gray-400 hover:text-gray-700 font-medium"
          >
            Cover letter →
          </Link>
        </div>
      </div>
    </div>
  )
}
