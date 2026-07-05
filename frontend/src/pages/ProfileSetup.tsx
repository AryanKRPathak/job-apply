import { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Loader2, Upload, X, CheckCircle2, User, Briefcase, MapPin, Sparkles, FileText,
  Shield, Ban, DollarSign,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { getProfile, createOrUpdateProfile, uploadResume } from '../api/profile'
import type { ResumeUploadResponse } from '../types/profile'

function TagInput({ label, values, onChange, placeholder, color = 'indigo' }: {
  label: string
  values: string[]
  onChange: (v: string[]) => void
  placeholder?: string
  color?: 'indigo' | 'red' | 'green'
}) {
  const [input, setInput] = useState('')

  const pillCls = {
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    green: 'bg-green-50 text-green-700 border-green-200',
  }[color]

  const btnCls = {
    indigo: 'bg-indigo-600 hover:bg-indigo-700',
    red: 'bg-red-500 hover:bg-red-600',
    green: 'bg-green-600 hover:bg-green-700',
  }[color]

  function add() {
    const v = input.trim()
    if (v && !values.includes(v)) onChange([...values, v])
    setInput('')
  }
  return (
    <div>
      {label && <label className="block text-sm font-semibold text-gray-800 mb-2">{label}</label>}
      <div className="flex flex-wrap gap-1.5 mb-2 min-h-[28px]">
        {values.map((v) => (
          <span key={v} className={`inline-flex items-center gap-1 border text-xs px-2.5 py-1 rounded-full font-medium ${pillCls}`}>
            {v}
            <button
              type="button"
              onClick={() => onChange(values.filter((x) => x !== v))}
              className="ml-0.5 opacity-70 hover:opacity-100"
            >
              <X size={10} />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), add())}
          placeholder={placeholder ?? 'Type and press Enter…'}
          className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
        />
        <button
          type="button"
          onClick={add}
          className={`px-4 py-2 text-sm text-white rounded-lg transition-colors font-medium ${btnCls}`}
        >
          Add
        </button>
      </div>
    </div>
  )
}

const emptyForm = {
  full_name: '',
  email: '',
  phone: '',
  target_titles: [] as string[],
  target_locations: [] as string[],
  skills: [] as string[],
  years_exp: '',
  story: '',
  company_blacklist: [] as string[],
  company_whitelist: [] as string[],
  title_keyword_blacklist: [] as string[],
  min_salary: '',
}

export default function ProfileSetup() {
  const qc = useQueryClient()
  const navigate = useNavigate()
  const [resumeResult, setResumeResult] = useState<ResumeUploadResponse | null>(null)
  const [dragging, setDragging] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [initialised, setInitialised] = useState(false)

  const { data: existingProfile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
    retry: false,
  })

  useEffect(() => {
    if (existingProfile && !initialised) {
      setForm({
        full_name: existingProfile.full_name ?? '',
        email: existingProfile.email ?? '',
        phone: existingProfile.phone ?? '',
        target_titles: existingProfile.target_titles ?? [],
        target_locations: existingProfile.target_locations ?? [],
        skills: existingProfile.skills ?? [],
        years_exp: existingProfile.years_exp ? String(existingProfile.years_exp) : '',
        story: existingProfile.story ?? '',
        company_blacklist: existingProfile.company_blacklist ?? [],
        company_whitelist: existingProfile.company_whitelist ?? [],
        title_keyword_blacklist: existingProfile.title_keyword_blacklist ?? [],
        min_salary: existingProfile.min_salary ? String(existingProfile.min_salary) : '',
      })
      setInitialised(true)
    }
  }, [existingProfile, initialised])

  const { mutate: uploadFile, isPending: uploading } = useMutation({
    mutationFn: (file: File) => uploadResume(file),
    onSuccess: (data) => {
      setResumeResult(data)
      setForm((f) => ({
        ...f,
        // Only fill fields that are currently empty
        full_name: f.full_name || data.full_name || f.full_name,
        email: f.email || data.email || f.email,
        phone: f.phone || data.phone || f.phone,
        years_exp: f.years_exp || (data.years_exp ? String(data.years_exp) : f.years_exp),
        story: f.story || data.story || f.story,
        target_titles: f.target_titles.length > 0 ? f.target_titles : data.suggested_titles,
        skills: [...new Set([...f.skills, ...data.detected_skills])],
      }))
      toast.success(`Resume parsed — ${data.detected_skills.length} skills detected`)
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: save, isPending: saving } = useMutation({
    mutationFn: () =>
      createOrUpdateProfile({
        ...form,
        years_exp: form.years_exp ? Number(form.years_exp) : undefined,
        min_salary: form.min_salary ? Number(form.min_salary) : undefined,
        resume_text: resumeResult?.extracted_text ?? existingProfile?.resume_text,
        resume_filename: resumeResult?.filename ?? existingProfile?.resume_filename,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Profile saved!')
      navigate('/dashboard')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file?.type === 'application/pdf') uploadFile(file)
      else toast.error('Please drop a PDF file')
    },
    [uploadFile],
  )

  const currentResumeName = resumeResult?.filename ?? existingProfile?.resume_filename

  if (profileLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={28} className="animate-spin text-indigo-600" />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Your Profile</h1>
        <p className="text-gray-500 mt-1">This is what the AI uses to score jobs and write your cover letters.</p>
      </div>

      {/* Resume Upload */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <FileText size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Resume</h2>
        </div>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
            dragging
              ? 'border-indigo-400 bg-indigo-50'
              : currentResumeName
              ? 'border-green-300 bg-green-50'
              : 'border-gray-200 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/40'
          }`}
        >
          {uploading ? (
            <div className="flex flex-col items-center gap-2 text-gray-500">
              <Loader2 size={28} className="animate-spin text-indigo-600" />
              <span className="text-sm">Parsing resume…</span>
            </div>
          ) : currentResumeName ? (
            <label className="cursor-pointer flex flex-col items-center gap-2">
              <CheckCircle2 size={28} className="text-green-500" />
              <span className="text-sm font-medium text-green-700">{currentResumeName}</span>
              <span className="text-xs text-gray-500">Click to replace</span>
              <input type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])} />
            </label>
          ) : (
            <label className="cursor-pointer flex flex-col items-center gap-3 text-gray-400">
              <Upload size={28} />
              <div>
                <p className="text-sm font-medium text-gray-600">Drop your resume PDF here</p>
                <p className="text-xs text-gray-400 mt-0.5">or click to browse</p>
              </div>
              <input type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])} />
            </label>
          )}
        </div>
        {resumeResult && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {resumeResult.detected_skills.slice(0, 10).map((s) => (
              <span key={s} className="text-xs bg-indigo-50 text-indigo-600 border border-indigo-100 px-2 py-0.5 rounded-full">{s}</span>
            ))}
            {resumeResult.detected_skills.length > 10 && (
              <span className="text-xs text-gray-400">+{resumeResult.detected_skills.length - 10} more added below</span>
            )}
          </div>
        )}
      </div>

      {/* Basic Info */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <User size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Basic Info</h2>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {([
            ['full_name', 'Full name', 'text', 'Jane Doe'],
            ['email', 'Email', 'email', 'jane@example.com'],
            ['phone', 'Phone', 'text', '+91 98765 43210'],
            ['years_exp', 'Years of experience', 'number', '3'],
          ] as const).map(([key, label, type, ph]) => (
            <div key={key}>
              <label className="block text-sm font-semibold text-gray-800 mb-1.5">{label}</label>
              <input
                type={type}
                value={(form as any)[key]}
                onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                placeholder={ph}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Job Preferences */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-5">
          <Briefcase size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Job Preferences</h2>
        </div>
        <div className="flex flex-col gap-5">
          <TagInput
            label="Target job titles"
            values={form.target_titles}
            onChange={(v) => setForm((f) => ({ ...f, target_titles: v }))}
            placeholder="e.g. Product Manager, Associate PM"
          />
          <TagInput
            label="Target locations"
            values={form.target_locations}
            onChange={(v) => setForm((f) => ({ ...f, target_locations: v }))}
            placeholder="e.g. Bangalore, Remote, Mumbai"
          />
        </div>
      </div>

      {/* Skills */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Skills</h2>
        </div>
        <TagInput
          label=""
          values={form.skills}
          onChange={(v) => setForm((f) => ({ ...f, skills: v }))}
          placeholder="e.g. Product Roadmap, SQL, Figma, Agile"
        />
      </div>

      {/* Smart Filters */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Shield size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Smart Filters</h2>
        </div>
        <p className="text-xs text-gray-400 mb-5">Jobs that don't pass these filters are skipped before AI scoring — saves time and API quota.</p>

        <div className="flex flex-col gap-6">
          {/* Company whitelist */}
          <div>
            <TagInput
              label="Company whitelist (only show jobs from these)"
              values={form.company_whitelist}
              onChange={(v) => setForm((f) => ({ ...f, company_whitelist: v }))}
              placeholder="e.g. Google, Razorpay, Meesho"
              color="green"
            />
            <p className="text-xs text-gray-400 mt-1">Leave empty to allow all companies.</p>
          </div>

          {/* Company blacklist */}
          <div>
            <TagInput
              label="Company blacklist (never show these)"
              values={form.company_blacklist}
              onChange={(v) => setForm((f) => ({ ...f, company_blacklist: v }))}
              placeholder="e.g. Infosys, Wipro, TCS"
              color="red"
            />
          </div>

          {/* Title keyword blacklist */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Ban size={13} className="text-red-500" />
              <label className="text-sm font-semibold text-gray-800">Title keyword blacklist</label>
            </div>
            <TagInput
              label=""
              values={form.title_keyword_blacklist}
              onChange={(v) => setForm((f) => ({ ...f, title_keyword_blacklist: v }))}
              placeholder="e.g. Senior Director, VP, 10+ years, Intern"
              color="red"
            />
            <p className="text-xs text-gray-400 mt-1">Jobs whose title contains any of these words are skipped.</p>
          </div>

          {/* Salary floor */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <DollarSign size={13} className="text-indigo-500" />
              <label className="text-sm font-semibold text-gray-800">Minimum salary (annual, in thousands)</label>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={form.min_salary}
                onChange={(e) => setForm((f) => ({ ...f, min_salary: e.target.value }))}
                placeholder="e.g. 800 for ₹8 LPA"
                className="w-56 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              {form.min_salary && (
                <span className="text-xs text-gray-500">
                  ₹{Number(form.min_salary).toLocaleString('en-IN')}k / year
                </span>
              )}
            </div>
            <p className="text-xs text-gray-400 mt-1">Only applied when a job lists a salary. Leave blank to ignore.</p>
          </div>
        </div>
      </div>

      {/* Story */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-8">
        <div className="flex items-center gap-2 mb-1">
          <MapPin size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Your Story</h2>
        </div>
        <p className="text-xs text-gray-400 mb-3">Used to personalize cover letters. Write 2–4 sentences about your background and goals.</p>
        <textarea
          rows={5}
          value={form.story}
          onChange={(e) => setForm((f) => ({ ...f, story: e.target.value }))}
          placeholder="e.g. I'm a product manager with 2 years of experience at a Series B startup. I led the 0→1 launch of our mobile app and grew MAU by 40%. Looking for a PM role at a product-first company in Bangalore…"
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      <div className="flex justify-end pb-8">
        <button
          onClick={() => save()}
          disabled={saving || !form.full_name}
          className="px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-colors shadow-sm"
        >
          {saving ? (
            <span className="flex items-center gap-2"><Loader2 size={14} className="animate-spin" /> Saving…</span>
          ) : (
            'Save Profile'
          )}
        </button>
      </div>
    </div>
  )
}
