import PlotlyComponent from 'react-plotly.js'
import { DEFAULT_LAYOUT, DEFAULT_CONFIG } from '../../utils/constants'

// Handle both ESM and CommonJS exports
const Plot = (PlotlyComponent as any).default || PlotlyComponent

interface ScatterData {
  x: number[]
  y: number[]
  text?: string[]
  name?: string
  mode?: 'markers' | 'lines' | 'lines+markers'
  marker?: {
    color?: string | string[]
    size?: number | number[]
    colorscale?: string
    showscale?: boolean
  }
}

interface ScatterChartProps {
  data: ScatterData[]
  title?: string
  xAxisTitle?: string
  yAxisTitle?: string
  height?: number
}

export function ScatterChart({
  data,
  title,
  xAxisTitle,
  yAxisTitle,
  height = 500,
}: ScatterChartProps) {
  return (
    <Plot
      data={data.map(series => ({
        type: 'scatter',
        mode: series.mode || 'markers',
        x: series.x,
        y: series.y,
        text: series.text,
        name: series.name,
        marker: series.marker,
        hovertemplate: '%{text}<br>%{xaxis.title.text}: %{x}<br>%{yaxis.title.text}: %{y}<extra></extra>',
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
        showlegend: data.length > 1,
      }}
      config={DEFAULT_CONFIG}
      style={{ width: '100%' }}
    />
  )
}
