import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UserPrefsState {
  selectedYear: string
  favoriteDrivers: string[]
  theme: 'light' | 'dark'
  setSelectedYear: (year: string) => void
  addFavoriteDriver: (driverId: string) => void
  removeFavoriteDriver: (driverId: string) => void
  setTheme: (theme: 'light' | 'dark') => void
}

const currentYear = new Date().getFullYear().toString()

// WITH localStorage persistence for user preferences
export const useUserPrefsStore = create<UserPrefsState>()(
  persist(
    (set) => ({
      selectedYear: currentYear,
      favoriteDrivers: [],
      theme: 'light',
      
      setSelectedYear: (year) => set({ selectedYear: year }),
      
      addFavoriteDriver: (driverId) => 
        set((state) => ({
          favoriteDrivers: [...new Set([...state.favoriteDrivers, driverId])]
        })),
      
      removeFavoriteDriver: (driverId) =>
        set((state) => ({
          favoriteDrivers: state.favoriteDrivers.filter(id => id !== driverId)
        })),
      
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'f1-dashboard-prefs', // localStorage key
    }
  )
)
