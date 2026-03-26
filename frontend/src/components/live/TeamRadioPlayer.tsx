import { memo, useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import { liveApi } from '../../api/live'
import type { TeamRadio, Driver } from '../../types/live'

export const TeamRadioPlayer = memo(() => {
  const sessionInfo = useLiveRaceStore((s) => s.sessionInfo)
  const drivers = useLiveRaceStore((s) => s.drivers)
  
  const [selectedDriver, setSelectedDriver] = useState<number | null>(null)
  const [sortBy, setSortBy] = useState<'timestamp' | 'driver'>('timestamp')
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null)
  const [playbackProgress, setPlaybackProgress] = useState<number>(0)
  const [volume, setVolume] = useState<number>(1)
  const [showNotification, setShowNotification] = useState<boolean>(false)
  const [notificationClip, setNotificationClip] = useState<TeamRadio | null>(null)
  
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const previousClipsCountRef = useRef<number>(0)

  // Fetch team radio clips
  const { data: radioClips = [], isLoading, error } = useQuery({
    queryKey: ['teamRadio', sessionInfo?.session_key],
    queryFn: () => liveApi.getTeamRadio(sessionInfo!.session_key),
    enabled: !!sessionInfo?.session_key,
    refetchInterval: sessionInfo?.mode === 'live' ? 30000 : false, // Refetch every 30s in live mode
  })

  // Show notification when new clip arrives in live mode
  useEffect(() => {
    if (sessionInfo?.mode === 'live' && radioClips.length > previousClipsCountRef.current) {
      const newClip = radioClips[0] // Assuming newest clip is first
      setNotificationClip(newClip)
      setShowNotification(true)
      
      // Hide notification after 5 seconds
      const timer = setTimeout(() => {
        setShowNotification(false)
      }, 5000)
      
      previousClipsCountRef.current = radioClips.length
      return () => clearTimeout(timer)
    }
    previousClipsCountRef.current = radioClips.length
  }, [radioClips, sessionInfo?.mode])

  // Update playback progress
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateProgress = () => {
      if (audio.duration) {
        setPlaybackProgress((audio.currentTime / audio.duration) * 100)
      }
    }

    const handleEnded = () => {
      setCurrentlyPlaying(null)
      setPlaybackProgress(0)
    }

    audio.addEventListener('timeupdate', updateProgress)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateProgress)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [currentlyPlaying])

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume
    }
  }, [volume])

  const getDriverInfo = (driverNumber: number): Driver | undefined => {
    return drivers.find(d => d.driver_number === driverNumber)
  }

  const handlePlayPause = (clip: TeamRadio) => {
    const audio = audioRef.current
    if (!audio) return

    if (currentlyPlaying === clip.recording_url) {
      // Pause current clip
      audio.pause()
      setCurrentlyPlaying(null)
    } else {
      // Play new clip
      audio.src = clip.recording_url
      audio.play()
      setCurrentlyPlaying(clip.recording_url)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio || !audio.duration) return

    const seekTime = (parseFloat(e.target.value) / 100) * audio.duration
    audio.currentTime = seekTime
    setPlaybackProgress(parseFloat(e.target.value))
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVolume(parseFloat(e.target.value))
  }

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatTimestamp = (date: string): string => {
    return new Date(date).toLocaleTimeString()
  }

  // Filter clips by selected driver
  const filteredClips = selectedDriver
    ? radioClips.filter((clip: TeamRadio) => clip.driver_number === selectedDriver)
    : radioClips

  // Sort clips
  const sortedClips = [...filteredClips].sort((a: TeamRadio, b: TeamRadio) => {
    if (sortBy === 'timestamp') {
      return new Date(b.date).getTime() - new Date(a.date).getTime()
    } else {
      // Sort by driver number
      return a.driver_number - b.driver_number
    }
  })

  if (isLoading) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Team Radio</h2>
        <div className="text-center text-gray-400 py-8">
          Loading radio clips...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Team Radio</h2>
        <div className="text-center text-red-500 py-8">
          Failed to load radio clips
        </div>
      </div>
    )
  }

  if (radioClips.length === 0) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Team Radio</h2>
        <div className="text-center text-gray-400 py-8">
          No radio clips available
        </div>
      </div>
    )
  }

  return (
    <div className="f1-panel flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-f1-border">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase">Team Radio</h2>
        <p className="text-sm text-gray-400 mt-1">{radioClips.length} clips</p>
      </div>

      {/* Notification for new clips */}
      {showNotification && notificationClip && (
        <div className="mx-4 mt-4 p-3 bg-f1-red/10 border-f1-red/20 border border-f1-red/30 rounded-lg flex items-center justify-between animate-pulse">
          <div className="flex items-center gap-2">
            <span className="text-f1-red">🔊</span>
            <span className="text-sm font-medium text-f1-red f1-text-glow">
              New radio from {getDriverInfo(notificationClip.driver_number)?.broadcast_name || `#${notificationClip.driver_number}`}
            </span>
          </div>
          <button
            onClick={() => setShowNotification(false)}
            className="text-f1-red hover:text-blue-800"
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      {/* Filters and Sort */}
      <div className="p-4 border-b border-f1-border space-y-3">
        {/* Driver Filter */}
        <div>
          <label htmlFor="driver-filter" className="block text-sm font-medium text-gray-300 mb-1">
            Filter by Driver
          </label>
          <select
            id="driver-filter"
            value={selectedDriver || ''}
            onChange={(e) => setSelectedDriver(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-3 py-2 border border-f1-border rounded-md focus:outline-none focus:ring-2 focus:ring-f1-red"
          >
            <option value="">All Drivers</option>
            {drivers.map((driver) => (
              <option key={driver.driver_number} value={driver.driver_number}>
                {driver.broadcast_name} (#{driver.driver_number})
              </option>
            ))}
          </select>
        </div>

        {/* Sort */}
        <div>
          <label htmlFor="sort-by" className="block text-sm font-medium text-gray-300 mb-1">
            Sort by
          </label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'timestamp' | 'driver')}
            className="w-full px-3 py-2 border border-f1-border rounded-md focus:outline-none focus:ring-2 focus:ring-f1-red"
          >
            <option value="timestamp">Timestamp (Newest First)</option>
            <option value="driver">Driver Number</option>
          </select>
        </div>
      </div>

      {/* Radio Clips List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[600px]">
        {sortedClips.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No clips match the selected filter
          </div>
        ) : (
          sortedClips.map((clip: TeamRadio, index: number) => {
            const driver = getDriverInfo(clip.driver_number)
            const isPlaying = currentlyPlaying === clip.recording_url
            
            return (
              <div
                key={`${clip.date}-${index}`}
                className="border border-f1-border rounded-lg p-3 hover:shadow-md transition-shadow"
                style={{
                  borderLeftWidth: '4px',
                  borderLeftColor: driver?.team_colour ? `#${driver.team_colour}` : '#6B7280'
                }}
              >
                {/* Clip Header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-f1-white">
                      {driver?.broadcast_name || `Driver #${clip.driver_number}`}
                    </span>
                    {driver && (
                      <span className="text-xs text-gray-400">
                        {driver.team_name}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-400">
                    {formatTimestamp(clip.date)}
                  </span>
                </div>

                {/* Duration */}
                <div className="text-sm text-gray-400 mb-2">
                  Duration: {formatDuration(clip.duration)}
                </div>

                {/* Playback Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handlePlayPause(clip)}
                    className="flex items-center justify-center w-10 h-10 rounded-full bg-f1-red f1-glow hover:bg-[#c00500] text-white transition-colors focus:outline-none focus:ring-2 focus:ring-f1-red focus:ring-offset-2"
                    aria-label={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? (
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>

                  {/* Progress Bar (only show when this clip is playing) */}
                  {isPlaying && (
                    <div className="flex-1">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={playbackProgress}
                        onChange={handleSeek}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-f1-red"
                        aria-label="Seek"
                      />
                    </div>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Global Audio Controls (when something is playing) */}
      {currentlyPlaying && (
        <div className="p-4 border-t border-f1-border bg-[#292a2c]/40">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-300">Volume</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-f1-red"
              aria-label="Volume"
            />
            <span className="text-sm text-gray-400 w-12 text-right">
              {Math.round(volume * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* Hidden Audio Element */}
      <audio ref={audioRef} preload="none" />
    </div>
  )
})

