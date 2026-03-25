// F1 Team Colors (2024 season)
export const F1_COLORS = {
  red_bull: '#3671C6',
  ferrari: '#E8002D',
  mercedes: '#27F4D2',
  mclaren: '#FF8000',
  aston_martin: '#229971',
  alpine: '#FF87BC',
  williams: '#64C4FF',
  rb: '#6692FF',
  kick_sauber: '#52E252',
  haas: '#B6BABD',
}

// F1 Brand Colors
export const F1_BRAND = {
  red: '#E10600',
  black: '#15151E',
  white: '#FFFFFF',
  gray: '#949498',
}

// Chart color palette for general use
export const CHART_COLORS = [
  '#E10600', // F1 Red
  '#3671C6', // Red Bull Blue
  '#E8002D', // Ferrari Red
  '#27F4D2', // Mercedes Teal
  '#FF8000', // McLaren Orange
  '#229971', // Aston Martin Green
  '#FF87BC', // Alpine Pink
  '#64C4FF', // Williams Blue
  '#6692FF', // RB Blue
  '#52E252', // Kick Sauber Green
]

// Plotly layout defaults
export const DEFAULT_LAYOUT = {
  font: {
    family: 'Inter, system-ui, sans-serif',
    size: 12,
  },
  paper_bgcolor: 'white',
  plot_bgcolor: '#f9fafb',
  margin: { t: 40, r: 20, b: 40, l: 60 },
  hovermode: 'closest' as const,
}

// Plotly config defaults
export const DEFAULT_CONFIG = {
  responsive: true,
  displayModeBar: true,
  displaylogo: false,
  modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
}
