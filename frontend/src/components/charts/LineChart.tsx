import PlotlyComponent from 'react-plotly.js'
import { DEFAULT_LAYOUT, DEFAULT_CONFIG } from '../../utils/constants'

// Handle both ESM and CommonJS exports
const Plot = (PlotlyComponent as any).default || PlotlyComponent

interface LineData {
  x: (string | number)[]
  y: number[]
  name: string
  mode?: 'lines' | 'markers' | 'lines+markers'
  line?: {
    color?: string
    width?: number
  }
  marker?: {
    color?: string
    size?: number
  }
}

interface LineChartProps {
  data: LineData[]
  title?: string
  xAxisTitle?: string
  yAxisTitle?: string
  height?: number
}

export function LineChart({
  data,
  title,
  xAxisTitle,
  yAxisTitle,
  height = 500,
}: LineChartProps) {
  return (
    <Plot
      data={data.map(series => ({
        type: 'scatter',
        mode: series.mode || 'lines+markers',
        x: series.x,
        y: series.y,
        name: series.name,
        line: series.line,
        marker: series.marker,
        hovertemplate: '%{y}<extra></extra>',
      }))}
      layout={{
        ...DEFAULT_LAYOUT,
        title: title || '',
        xaxis: {
          title: xAxisTitle || '',
          gridcolor: '#e5e7eb',
        },
        yaxis: {
          title: yAxisTitle || '',
          gridcolor: '#e5e7eb',
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
