import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { tokenStore } from './lib/api'

// Business Intelligence
import BIDashboard from './pages/BIDashboard'
import DataExplorer from './pages/DataExplorer'
import Appointments from './pages/Appointments'
import ExcelImport from './pages/ExcelImport'

// Operations & Logistics (adapted from V1)
import Queue from './pages/Queue'
import Live from './pages/Live'
import Requests from './pages/Requests'
import RequestDetail from './pages/RequestDetail'
import NewRequest from './pages/NewRequest'
import Fleet from './pages/Fleet'
import Garage from './pages/Garage'

// Engineering
import Architecture from './pages/Architecture'
import Simulations from './pages/Simulations'

// Public
import Login from './pages/Login'
import PublicIntake from './pages/PublicIntake'

const Guard = ({ children }: { children: React.ReactElement }) =>
  tokenStore.get() ? children : <Navigate to="/login" replace />

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/demande" element={<PublicIntake />} />
        <Route path="/" element={<Guard><Layout /></Guard>}>
          {/* BI & Decision Support */}
          <Route index element={<BIDashboard />} />
          <Route path="data" element={<DataExplorer />} />
          <Route path="appointments" element={<Appointments />} />
          <Route path="excel" element={<ExcelImport />} />
          {/* Operations & Logistics */}
          <Route path="queue" element={<Queue />} />
          <Route path="live" element={<Live />} />
          <Route path="requests" element={<Requests />} />
          <Route path="requests/:id" element={<RequestDetail />} />
          <Route path="new" element={<NewRequest />} />
          <Route path="fleet" element={<Fleet />} />
          <Route path="garage" element={<Garage />} />
          {/* Engineering */}
          <Route path="architecture" element={<Architecture />} />
          <Route path="simulations" element={<Simulations />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
