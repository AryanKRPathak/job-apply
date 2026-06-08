import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import JobDetail from './pages/JobDetail'
import OutreachPage from './pages/OutreachPage'
import ProfileSetup from './pages/ProfileSetup'
import ScheduleSettings from './pages/ScheduleSettings'
import QuestionBankPage from './pages/QuestionBankPage'
import AnalyticsPage from './pages/AnalyticsPage'
import Layout from './components/Layout'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/profile" element={<ProfileSetup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
          <Route path="/schedule" element={<ScheduleSettings />} />
          <Route path="/outreach/:jobId" element={<OutreachPage />} />
          <Route path="/questions" element={<QuestionBankPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
