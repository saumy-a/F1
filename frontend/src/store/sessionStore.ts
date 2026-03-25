import { create } from 'zustand'
import type { SessionInfo } from '../types/live'

interface SessionState {
  currentSession: SessionInfo | null
  sessionMode: 'live' | 'upcoming' | 'replay' | null
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  setCurrentSession: (session: SessionInfo | null) => void
  setSessionMode: (mode: 'live' | 'upcoming' | 'replay' | null) => void
  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected' | 'error') => void
  reset: () => void
}

const initialState = {
  currentSession: null,
  sessionMode: null,
  connectionStatus: 'disconnected' as const,
}

// NO localStorage persistence for session data
export const useSessionStore = create<SessionState>((set) => ({
  ...initialState,
  
  setCurrentSession: (session) => set({ currentSession: session }),
  
  setSessionMode: (mode) => set({ sessionMode: mode }),
  
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  
  reset: () => set(initialState),
}))
