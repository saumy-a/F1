export interface CircuitDetails {
  id: string
  length: string
  laps: string
  distance: string
  drsZones: string
  lapRecord: string
  imageUrl: string
}

export const circuitDetailsMap: Record<string, CircuitDetails> = {
  'Monte Carlo': {
    id: 'monaco',
    length: '3.337',
    laps: '78',
    distance: '260.286',
    drsZones: '1',
    lapRecord: '1:12.909 (Lewis Hamilton, 2021)',
    imageUrl: 'https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Monaco_Circuit.png.transform/8col/image.png'
  },
  'Silverstone': {
    id: 'silverstone',
    length: '5.891',
    laps: '52',
    distance: '306.198',
    drsZones: '2',
    lapRecord: '1:27.097 (Max Verstappen, 2020)',
    imageUrl: 'https://media.formula1.com/image/upload/f_auto/q_auto/v1677244987/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Great_Britain_Circuit.png.transform/8col/image.png'
  },
  'Melbourne': {
    id: 'melbourne',
    length: '5.278',
    laps: '58',
    distance: '306.124',
    drsZones: '4',
    lapRecord: '1:19.813 (Charles Leclerc, 2024)',
    imageUrl: 'https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Australia_Circuit.png.transform/8col/image.png'
  },
  'Monza': {
    id: 'monza',
    length: '5.793',
    laps: '53',
    distance: '306.720',
    drsZones: '2',
    lapRecord: '1:21.046 (Rubens Barrichello, 2004)',
    imageUrl: 'https://media.formula1.com/image/upload/f_auto/q_auto/v1677244987/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Italy_Circuit.png.transform/8col/image.png'
  },
  'Spa-Francorchamps': {
    id: 'spa',
    length: '7.004',
    laps: '44',
    distance: '308.052',
    drsZones: '2',
    lapRecord: '1:46.286 (Valtteri Bottas, 2018)',
    imageUrl: 'https://media.formula1.com/image/upload/f_auto/q_auto/v1677244985/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Belgium_Circuit.png.transform/8col/image.png'
  }
}
