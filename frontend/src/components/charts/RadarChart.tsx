import PlotlyComponent from 'react-plotly.js'
import { DEFAULT_LAYOUT, DEFAULT_CONFIG } from '../../utils/constants'

// Handle both ESM and CommonJS exports
const Plot = (PlotlyComponent as any).default || PlotlyComponent

interface RadarData {
  r: number[]
  theta: string[]
  name: string
  fill?: 'toself' | 'tonext' | 'none'
  fillcolor?: string
  line?: {
    color?: string
  }
}

interface RadarChartProps {
  data: RadarData[]
  title?: string
  height?: number
}

export function RadarChart({ data, title, height = 500 }: RadarChartProps) {
  return (
    <Plot
      data={data.map(series => ({
        type: 'scatterpolar',
        r: series.r,
        theta: series.theta,
        name: series.name,
        fill: series.fill || 'toself',
        fillcolor: series.fillcolor,
        line: series.line,
      }))}
      layout={{
        ...DEFAULT_LAYOUT,
        title: title || '',
        polar: {
          radialaxis: {
            visible: true,
            range: [0, 100],
            gridcolor: '#e5e7eb',
          },
          angularaxis: {
            gridcolor: '#e5e7eb',
          },
        },
        height,
        showlegend: true,
        legend: {
          x: 1,
          xanchor: 'right',
          y: 1,
        },
      }}
      config={DEFAULT_CONFIG}
      style={{ width: '100%' }}
    />
  )
}
