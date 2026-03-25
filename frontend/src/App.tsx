import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { LoadingSpinner } from './components/shared/LoadingSpinner'

// Lazy-loaded pages for code splitting
const OverviewPage = lazy(() => import('./pages/OverviewPage'))
const DriverStandingsPage = lazy(() => import('./pages/DriverStandingsPage'))
const ConstructorStandingsPage = lazy(() => import('./pages/ConstructorStandingsPage'))
const CalendarPage = lazy(() => import('./pages/CalendarPage'))
const RacesPage = lazy(() => import('./pages/RacesPage'))
const HeadToHeadPage = lazy(() => import('./pages/HeadToHeadPage'))
const QualifyingPage = lazy(() => import('./pages/QualifyingPage'))
const ChampionshipPage = lazy(() => import('./pages/ChampionshipPage'))
const LapTimesPage = lazy(() => import('./pages/LapTimesPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const LiveTrackerPage = lazy(() => import('./pages/LiveTrackerPage'))

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/standings/drivers" element={<DriverStandingsPage />} />
            <Route path="/standings/constructors" element={<ConstructorStandingsPage />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/races" element={<RacesPage />} />
            <Route path="/head-to-head" element={<HeadToHeadPage />} />
            <Route path="/qualifying" element={<QualifyingPage />} />
            <Route path="/championship" element={<ChampionshipPage />} />
            <Route path="/lap-times" element={<LapTimesPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/live" element={<LiveTrackerPage />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  )
}

export default App
