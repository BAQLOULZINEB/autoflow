import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { tokenStore } from './lib/api'
import Architecture from './pages/Architecture'
import Dashboard from './pages/Dashboard'
import Fleet from './pages/Fleet'
import Live from './pages/Live'
import Login from './pages/Login'
import NewRequest from './pages/NewRequest'
import PublicIntake from './pages/PublicIntake'
import Queue from './pages/Queue'
import RequestDetail from './pages/RequestDetail'
import Requests from './pages/Requests'
import Simulations from './pages/Simulations'

const Guard = ({ children }: { children: React.ReactElement }) => tokenStore.get() ? children : <Navigate to="/login" replace />

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/demande" element={<PublicIntake />} />
        <Route path="/" element={<Guard><Layout /></Guard>}>
          <Route index element={<Dashboard />} />
          <Route path="queue" element={<Queue />} />
          <Route path="live" element={<Live />} />
          <Route path="simulations" element={<Simulations />} />
          <Route path="requests" element={<Requests />} />
          <Route path="requests/:id" element={<RequestDetail />} />
          <Route path="new" element={<NewRequest />} />
          <Route path="fleet" element={<Fleet />} />
          <Route path="architecture" element={<Architecture />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
