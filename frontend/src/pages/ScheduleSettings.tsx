import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Loader2, Plus, Trash2 } from 'lucide-react'
import { getSchedules, createSchedule, updateSchedule, deleteSchedule } from '../api/schedule'
import { getProfile } from '../api/profile'

const PORTALS = ['indeed', 'linkedin', 'naukri']
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const DAY_CRON = ['1', '2', '3', '4', '5', '6', '0']

export default function ScheduleSettings() {
  const qc = useQueryClient()
  const [selectedDays, setSelectedDays] = useState<string[]>(['1', '2', '3', '4', '5'])
  const [hour, setHour] = useState('9')
  const [minute, setMinute] = useState('0')
  const [portals, setPortals] = useState<string[]>(['indeed', 'linkedin', 'naukri'])

  const { data: schedules, isLoading } = useQuery({ queryKey: ['schedules'], queryFn: getSchedules })

  const { mutate: create, isPending: creating } = useMutation({
    mutationFn: async () => {
      const profile = await getProfile()
      const dow = selectedDays.length === 7 ? '*' : selectedDays.join(',')
      const cron = `${minute} ${hour} * * ${dow}`
      return createSchedule({ profile_id: profile.id, cron_expression: cron, portals })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['schedules'] })
      toast.success('Schedule created')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: toggle } = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      updateSchedule(id, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['schedules'] }),
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: remove } = useMutation({
    mutationFn: (id: string) => deleteSchedule(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['schedules'] })
      toast.success('Schedule deleted')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  function toggleDay(d: string) {
    setSelectedDays((prev) =>
      prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d],
    )
  }

  function togglePortal(p: string) {
    setPortals((prev) => (prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]))
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Scheduled Scraping</h1>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-base font-semibold text-gray-800 mb-4">Create new schedule</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Days</label>
          <div className="flex gap-2 flex-wrap">
            {DAYS.map((label, i) => (
              <button
                key={label}
                onClick={() => toggleDay(DAY_CRON[i])}
                className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                  selectedDays.includes(DAY_CRON[i])
                    ? 'bg-brand-600 text-white border-brand-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-brand-300'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hour (0–23)</label>
            <input
              type="number"
              min={0}
              max={23}
              value={hour}
              onChange={(e) => setHour(e.target.value)}
              className="w-20 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Minute (0–59)</label>
            <input
              type="number"
              min={0}
              max={59}
              value={minute}
              onChange={(e) => setMinute(e.target.value)}
              className="w-20 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
        </div>

        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-700 mb-2">Portals</label>
          <div className="flex gap-2">
            {PORTALS.map((p) => (
              <button
                key={p}
                onClick={() => togglePortal(p)}
                className={`px-3 py-1.5 text-sm rounded-lg border capitalize transition-colors ${
                  portals.includes(p)
                    ? 'bg-brand-600 text-white border-brand-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-brand-300'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => create()}
          disabled={creating || selectedDays.length === 0 || portals.length === 0}
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm rounded-lg disabled:opacity-60 transition-colors"
        >
          {creating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
          Create schedule
        </button>
      </div>

      <div className="flex flex-col gap-3">
        {isLoading && <div className="flex justify-center py-8"><Loader2 size={22} className="animate-spin text-brand-600" /></div>}
        {(schedules ?? []).map((s: any) => (
          <div key={s.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-mono text-gray-800">{s.cron_expression}</p>
              <p className="text-xs text-gray-500 mt-0.5 capitalize">
                Portals: {(s.portals ?? []).join(', ')}
              </p>
              {s.last_run_at && (
                <p className="text-xs text-gray-400">Last run: {new Date(s.last_run_at).toLocaleString()}</p>
              )}
            </div>
            <button
              onClick={() => toggle({ id: s.id, is_active: !s.is_active })}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                s.is_active
                  ? 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100'
                  : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100'
              }`}
            >
              {s.is_active ? 'Active' : 'Paused'}
            </button>
            <button
              onClick={() => remove(s.id)}
              className="text-gray-400 hover:text-red-500 transition-colors"
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}
        {!isLoading && (schedules ?? []).length === 0 && (
          <p className="text-center text-gray-400 py-8">No schedules yet.</p>
        )}
      </div>
    </div>
  )
}
