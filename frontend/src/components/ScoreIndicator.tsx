interface Props {
  score: number | null
}

export default function ScoreIndicator({ score }: Props) {
  if (score === null || score === undefined)
    return <span className="text-xs text-gray-300 font-medium">—</span>

  const label = score >= 80 ? 'Strong' : score >= 60 ? 'Good' : 'Weak'
  const style =
    score >= 80
      ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
      : score >= 60
        ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
        : 'bg-red-50 text-red-600 border border-red-100'

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full ${style}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${score >= 80 ? 'bg-emerald-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-400'}`} />
      {score} · {label}
    </span>
  )
}
