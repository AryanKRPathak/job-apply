import { clsx } from 'clsx'

const styles: Record<string, string> = {
  saved:      'bg-gray-100 text-gray-600 border-gray-200',
  applied:    'bg-blue-50 text-blue-700 border-blue-200',
  interview:  'bg-amber-50 text-amber-700 border-amber-200',
  rejected:   'bg-red-50 text-red-600 border-red-200',
  offer:      'bg-emerald-50 text-emerald-700 border-emerald-200',
}

const statuses = ['saved', 'applied', 'interview', 'rejected', 'offer']

interface Props {
  status: string
  onChange: (status: string) => void
}

export default function StatusDropdown({ status, onChange }: Props) {
  return (
    <select
      value={status}
      onChange={(e) => onChange(e.target.value)}
      className={clsx(
        'text-xs font-semibold rounded-full px-3 py-1 border cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-400 appearance-none',
        styles[status] ?? styles.saved,
      )}
    >
      {statuses.map((s) => (
        <option key={s} value={s}>
          {s.charAt(0).toUpperCase() + s.slice(1)}
        </option>
      ))}
    </select>
  )
}
