import { useUserPrefsStore } from '../../store/userPrefsStore'

export function YearSelector() {
  const { selectedYear, setSelectedYear } = useUserPrefsStore()
  
  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: currentYear - 1950 + 1 }, (_, i) => currentYear - i)
  
  return (
    <select
      value={selectedYear}
      onChange={(e) => setSelectedYear(e.target.value)}
      className="px-3 py-2 border border-f1-border rounded-md shadow-sm focus:outline-none focus:ring-f1-red focus:border-f1-red"
    >
      {years.map((year) => (
        <option key={year} value={year.toString()}>
          {year}
        </option>
      ))}
    </select>
  )
}
