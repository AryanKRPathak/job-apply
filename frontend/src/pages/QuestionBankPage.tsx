import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, ChevronDown, ChevronUp, Loader2, BookOpen, Pencil, Check, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { getProfile } from '../api/profile'
import { getQuestions, createQuestion, updateQuestion, deleteQuestion } from '../api/question_bank'
import type { QuestionBank } from '../types/question_bank'

const CATEGORIES = ['Background', 'Motivation', 'Strengths', 'Challenges', 'Situational', 'Technical', 'Other']

function QuestionCard({ q, onUpdate, onDelete }: {
  q: QuestionBank
  onUpdate: (id: string, data: Partial<QuestionBank>) => void
  onDelete: (id: string) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState({ question: q.question, answer: q.answer ?? '', category: q.category ?? '' })

  function saveEdit() {
    onUpdate(q.id, { question: draft.question, answer: draft.answer || null, category: draft.category || null })
    setEditing(false)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
      <div
        className="flex items-start justify-between gap-3 p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => !editing && setExpanded((e) => !e)}
      >
        <div className="flex-1 min-w-0">
          {editing ? (
            <input
              value={draft.question}
              onChange={(e) => setDraft((d) => ({ ...d, question: e.target.value }))}
              onClick={(e) => e.stopPropagation()}
              className="w-full text-sm font-medium px-2 py-1 border border-indigo-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          ) : (
            <p className="text-sm font-medium text-gray-900 leading-snug">{q.question}</p>
          )}
          {q.category && !editing && (
            <span className="inline-block mt-1.5 text-xs bg-indigo-50 text-indigo-600 border border-indigo-100 px-2 py-0.5 rounded-full">
              {q.category}
            </span>
          )}
          {editing && (
            <select
              value={draft.category}
              onChange={(e) => setDraft((d) => ({ ...d, category: e.target.value }))}
              onClick={(e) => e.stopPropagation()}
              className="mt-2 text-xs border border-gray-300 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">No category</option>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          )}
        </div>
        <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
          {editing ? (
            <>
              <button onClick={saveEdit} className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg transition-colors">
                <Check size={14} />
              </button>
              <button onClick={() => setEditing(false)} className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors">
                <X size={14} />
              </button>
            </>
          ) : (
            <>
              <button onClick={() => { setEditing(true); setExpanded(true) }} className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                <Pencil size={14} />
              </button>
              <button onClick={() => onDelete(q.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                <Trash2 size={14} />
              </button>
              <button onClick={() => setExpanded((e) => !e)} className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors">
                {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </>
          )}
        </div>
      </div>

      {(expanded || editing) && (
        <div className="px-4 pb-4 border-t border-gray-100 pt-3">
          {editing ? (
            <textarea
              value={draft.answer}
              onChange={(e) => setDraft((d) => ({ ...d, answer: e.target.value }))}
              rows={4}
              placeholder="Write your answer here…"
              className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          ) : q.answer ? (
            <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{q.answer}</p>
          ) : (
            <p className="text-xs text-gray-400 italic">No answer yet. Click the pencil to add one.</p>
          )}
        </div>
      )}
    </div>
  )
}

export default function QuestionBankPage() {
  const qc = useQueryClient()
  const [newQ, setNewQ] = useState('')
  const [newCat, setNewCat] = useState('')
  const [filterCat, setFilterCat] = useState('')

  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getProfile, retry: false })

  const { data: questions = [], isLoading } = useQuery({
    queryKey: ['questions', profile?.id],
    queryFn: () => getQuestions(profile!.id),
    enabled: !!profile?.id,
  })

  const { mutate: addQ, isPending: adding } = useMutation({
    mutationFn: () => createQuestion({ profile_id: profile!.id, question: newQ.trim(), category: newCat || null }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['questions'] })
      setNewQ('')
      setNewCat('')
      toast.success('Question added')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: editQ } = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<QuestionBank> }) => updateQuestion(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['questions'] }),
    onError: (e: Error) => toast.error(e.message),
  })

  const { mutate: removeQ } = useMutation({
    mutationFn: deleteQuestion,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['questions'] })
      toast.success('Deleted')
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const filtered = filterCat ? questions.filter((q) => q.category === filterCat) : questions
  const answered = questions.filter((q) => q.answer && q.answer.trim().length > 0).length

  if (!profile) {
    return (
      <div className="text-center py-24">
        <p className="text-gray-500">Set up your profile first to use the question bank.</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Question Bank</h1>
        <p className="text-gray-500 mt-1">Store your answers to common application questions so you never start from scratch.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p className="text-2xl font-bold text-gray-900">{questions.length}</p>
          <p className="text-xs text-gray-500 mt-0.5">Total questions</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p className="text-2xl font-bold text-green-600">{answered}</p>
          <p className="text-xs text-gray-500 mt-0.5">Answered</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
          <p className="text-2xl font-bold text-amber-500">{questions.length - answered}</p>
          <p className="text-xs text-gray-500 mt-0.5">Need answers</p>
        </div>
      </div>

      {/* Add question */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-800 mb-3">Add a question</h2>
        <div className="flex flex-col gap-2">
          <input
            value={newQ}
            onChange={(e) => setNewQ(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && newQ.trim() && addQ()}
            placeholder="e.g. Tell me about yourself. Why do you want to join us?"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div className="flex gap-2">
            <select
              value={newCat}
              onChange={(e) => setNewCat(e.target.value)}
              className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="">No category</option>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <button
              onClick={() => newQ.trim() && addQ()}
              disabled={adding || !newQ.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {adding ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Filter */}
      {questions.length > 0 && (
        <div className="flex items-center gap-3 mb-4">
          <span className="text-sm text-gray-500">Filter:</span>
          <select
            value={filterCat}
            onChange={(e) => setFilterCat(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option value="">All categories</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          {filterCat && (
            <button onClick={() => setFilterCat('')} className="text-xs text-indigo-600 hover:underline">
              Clear
            </button>
          )}
        </div>
      )}

      {/* Questions */}
      {isLoading ? (
        <div className="flex justify-center py-24">
          <Loader2 size={28} className="animate-spin text-indigo-600" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-24 bg-white rounded-2xl border border-dashed border-gray-200">
          <BookOpen size={36} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">No questions yet</p>
          <p className="text-sm text-gray-400 mt-1">Add common interview questions and your go-to answers above.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map((q) => (
            <QuestionCard
              key={q.id}
              q={q}
              onUpdate={(id, data) => editQ({ id, data })}
              onDelete={removeQ}
            />
          ))}
        </div>
      )}
    </div>
  )
}
