import React, { useMemo } from 'react'
import Plot from 'react-plotly.js'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { Data, Layout, Config } from 'plotly.js'

export const GapTrackerChart = React.memo(function GapTrackerChart() {
  const intervalHistory = useLiveRaceStore((state) => state.intervalHistory)
  const drivers = useLiveRaceStore((state) => state.drivers)
  
  // Group interval history by driver and create chart traces
  const chartData = useMemo(() => {
    if (intervalHistory.length === 0 || drivers.length === 0) {
      return []
    }
    
    // Group by driver number
    const driverDataMap = new Map<number, { laps: number[]; gaps: number[] }>()
    
    intervalHistory.forEach((entry) => {
      if (!driverDataMap.has(entry.driver_number)) {
        driverDataMap.set(entry.driver_number, { laps: [], gaps: [] })
      }
      
      const driverData = driverDataMap.get(entry.driver_number)!
      driverData.laps.push(entry.lap)
      
      // Convert gap to number, handle null/string cases
      let gapValue = 0
      if (entry.gap === null) {
        gapValue = 0
      } else if (typeof entry.gap === 'string') {
        // Handle "+1 LAP" format - assign large value for lapped cars
        gapValue = 999
      } else {
        gapValue = entry.gap
      }
      
      driverData.gaps.push(gapValue)
    })
    
    // Create Plotly traces for each driver
    const traces: Data[] = Array.from(driverDataMap.entries()).map(([driverNum, data]) => {
      const driver = drivers.find((d) => d.driver_number === driverNum)
      
      return {
        x: data.laps,
        y: data.gaps,
        type: 'scatter',
        mode: 'lines',
        name: driver?.broadcast_name || `#${driverNum}`,
        line: {
          color: driver?.team_colour ? `#${driver.team_colour}` : '#999999',
          width: 2
        },
        hovertemplate: `<b>${driver?.broadcast_name || `#${driverNum}`}</b><br>` +
                      'Lap: %{x}<br>' +
                      'Gap: %{y:.3f}s<br>' +
                      '<extra></extra>'
      } as Data
    })
    
    return traces
  }, [intervalHistory, drivers])
  
  const layout: Partial<Layout> = useMemo(() => ({
    xaxis: { 
      title: 'Lap Number',
      gridcolor: '#e5e7eb'
    },
    yaxis: { 
      title: 'Gap to Leader (seconds)',
      gridcolor: '#e5e7eb'
    },
    hovermode: 'closest',
    showlegend: true,
    legend: { 
      orientation: 'h', 
      y: -0.2,
      x: 0,
      xanchor: 'left'
    },
    margin: { l: 60, r: 20, t: 20, b: 80 },
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    autosize: true
  }), [])
  
  const config: Partial<Config> = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    scrollZoom: true
  }
  
  return (
    <div className="f1-panel">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold">
        Gap to Leader
      </div>
      
      <div className="p-4">
        {chartData.length === 0 ? (
          <div className="flex items-center justify-center h-[300px] md:h-[350px] lg:h-[400px] text-gray-400">
            No gap data available
          </div>
        ) : (
          <Plot
            data={chartData}
            layout={layout}
            config={config}
            className="w-full h-[300px] md:h-[350px] lg:h-[400px]"
            useResizeHandler={true}
            style={{ width: '100%', height: '100%' }}
          />
        )}
      </div>
    </div>
  )
})
