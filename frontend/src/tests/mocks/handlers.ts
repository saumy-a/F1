import { http, HttpResponse } from 'msw'

const API_BASE_URL = 'http://localhost:8000'

// Mock data - matches backend response format (array of standings)
const mockDriverStandings = [
  {
    position: '1',
    points: '575',
    wins: '19',
    Driver: {
      driverId: 'max_verstappen',
      givenName: 'Max',
      familyName: 'Verstappen',
      nationality: 'Dutch',
    },
    Constructors: [
      {
        constructorId: 'red_bull',
        name: 'Red Bull',
        nationality: 'Austrian',
      },
    ],
  },
  {
    position: '2',
    points: '285',
    wins: '2',
    Driver: {
      driverId: 'perez',
      givenName: 'Sergio',
      familyName: 'Pérez',
      nationality: 'Mexican',
    },
    Constructors: [
      {
        constructorId: 'red_bull',
        name: 'Red Bull',
        nationality: 'Austrian',
      },
    ],
  },
]

const mockConstructorStandings = [
  {
    position: '1',
    points: '860',
    wins: '21',
    Constructor: {
      constructorId: 'red_bull',
      name: 'Red Bull',
      nationality: 'Austrian',
    },
  },
  {
    position: '2',
    points: '409',
    wins: '1',
    Constructor: {
      constructorId: 'mercedes',
      name: 'Mercedes',
      nationality: 'German',
    },
  },
]

const mockRaceSchedule = [
  {
    season: '2024',
    round: '1',
    raceName: 'Bahrain Grand Prix',
    Circuit: {
      circuitId: 'bahrain',
      circuitName: 'Bahrain International Circuit',
      Location: {
        lat: '26.0325',
        long: '50.5106',
        locality: 'Sakhir',
        country: 'Bahrain',
      },
    },
    date: '2024-03-02',
    time: '15:00:00Z',
  },
]

export const handlers = [
  // Driver standings
  http.get(`${API_BASE_URL}/api/standings/drivers/:year`, () => {
    return HttpResponse.json(mockDriverStandings)
  }),

  // Constructor standings
  http.get(`${API_BASE_URL}/api/standings/constructors/:year`, () => {
    return HttpResponse.json(mockConstructorStandings)
  }),

  // Race schedule
  http.get(`${API_BASE_URL}/api/races/:year`, () => {
    return HttpResponse.json(mockRaceSchedule)
  }),
]
