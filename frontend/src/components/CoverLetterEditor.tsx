import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { updateCoverLetter } from '../api/jobs'

interface Props {
  jobId: string
  initial: string | null
}

export default function CoverLetterEditor({ jobId, initial }: Props) {
  const [text, setText] = useState(initial ?? '')
  const qc = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: () => updateCoverLetter(jobId, text),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['job', jobId] })
      toast.success('Cover letter saved')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  return (
    <div className="flex flex-col gap-3">
      <textarea
        className="w-full min-h-[300px] rounded-lg border border-gray-200 p-4 text-sm font-mono resize-y focus:outline-none focus:ring-2 focus:ring-brand-500"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="AI-generated cover letter will appear here..."
      />
      <div className="flex justify-end">
        <button
          disabled={isPending}
          onClick={() => mutate()}
          className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm rounded-lg disabled:opacity-50 transition-colors"
        >
          {isPending ? 'Saving…' : 'Save cover letter'}
        </button>
      </div>
    </div>
  )
}
