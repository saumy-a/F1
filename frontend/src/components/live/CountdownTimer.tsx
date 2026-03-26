import { useState, useEffect } from 'react'

interface CountdownTimerProps {
  startTime: string
}

interface TimeRemaining {
  days: number
  hours: number
  minutes: number
  seconds: number
}

export function CountdownTimer({ startTime }: CountdownTimerProps) {
  const [timeRemaining, setTimeRemaining] = useState<TimeRemaining | null>(null)
  
  useEffect(() => {
    const calculateTimeRemaining = () => {
      const now = new Date()
      const start = new Date(startTime)
      const diff = start.getTime() - now.getTime()
      
      if (diff <= 0) {
        setTimeRemaining({ days: 0, hours: 0, minutes: 0, seconds: 0 })
        return
      }
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)
      
      setTimeRemaining({ days, hours, minutes, seconds })
    }
    
    calculateTimeRemaining()
    const interval = setInterval(calculateTimeRemaining, 1000)
    
    return () => clearInterval(interval)
  }, [startTime])
  
  if (!timeRemaining) return null
  
  // Calculate total hours remaining for red highlight condition
  const totalHoursRemaining = timeRemaining.days * 24 + timeRemaining.hours
  const isUrgent = totalHoursRemaining < 1
  const isCritical = isUrgent && timeRemaining.minutes < 5
  const isZero = timeRemaining.days === 0 && timeRemaining.hours === 0 && 
                 timeRemaining.minutes === 0 && timeRemaining.seconds === 0
  
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Session Starts In</h3>
      
      <div className={`grid grid-cols-4 gap-4 ${isCritical ? 'animate-pulse' : ''}`}>
        <TimeUnit value={timeRemaining.days} label="Days" urgent={isUrgent} />
        <TimeUnit value={timeRemaining.hours} label="Hours" urgent={isUrgent} />
        <TimeUnit value={timeRemaining.minutes} label="Minutes" urgent={isUrgent} />
        <TimeUnit value={timeRemaining.seconds} label="Seconds" urgent={isUrgent} />
      </div>
      
      {isZero && (
        <div className="mt-4 text-center text-lg font-semibold text-red-600">
          Session starting...
        </div>
      )}
    </div>
  )
}

interface TimeUnitProps {
  value: number
  label: string
  urgent: boolean
}

function TimeUnit({ value, label, urgent }: TimeUnitProps) {
  return (
    <div className={`text-center p-4 rounded-lg ${urgent ? 'bg-red-100' : 'bg-gray-100'}`}>
      <div className={`text-3xl font-display text-f1-white tracking-wider uppercase ${urgent ? 'text-red-600' : 'text-f1-white'}`}>
        {value.toString().padStart(2, '0')}
      </div>
      <div className="text-sm text-gray-400 mt-1">{label}</div>
    </div>
  )
}
