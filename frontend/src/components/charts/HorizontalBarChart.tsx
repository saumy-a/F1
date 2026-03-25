import PlotlyComponent from 'react-plotly.js'
import { DEFAULT_LAYOUT, DEFAULT_CONFIG } from '../../utils/constants'

// Handle both ESM and CommonJS exports
const Plot = (PlotlyComponent as any).default || PlotlyComponent

interface HorizontalBarChartProps {
  data: {
    x: number[]
    y: string[]
    text?: string[]
    marker?: {
      color?: string | string[]
    }
  }
  title?: string
  xAxisTitle?: string
  yAxisTitle?: string
  height?: number
}

export function HorizontalBarChart({
  data,
  title,
  xAxisTitle,
  yAxisTitle,
  height = 500,
}: HorizontalBarChartProps) {
  return (
    <Plot
      data={[
        {
          type: 'bar',
          orientation: 'h',
          x: data.x,
          y: data.y,
          text: data.text,
          textposition: 'auto',
          marker: data.marker,
          hovertemplate: '%{y}: %{x}<extra></extra>',
        },
      ]}
      layout={{
        ...DEFAULT_LAYOUT,
        title: title || '',
        xaxis: {
          title: xAxisTitle || '',
          gridcolor: '#e5e7eb',
        },
        yaxis: {
          title: yAxisTitle || '',
          autorange: 'reversed',
        },
        height,
      }}
      config={DEFAULT_CONFIG}
      style={{ width: '100%' }}
    />
  )
}
