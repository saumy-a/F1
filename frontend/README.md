# F1 Dashboard Frontend

Modern React + TypeScript frontend for the F1 Dashboard application.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management
- **Axios** - HTTP client
- **Plotly.js** - Interactive charts
- **Tailwind CSS** - Styling
- **Vitest** - Testing framework

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Test

```bash
npm run test
```

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## Project Structure

```
src/
├── api/              # API client and request functions
├── components/       # React components
│   ├── layout/      # Layout components (Header, Sidebar, Footer)
│   ├── shared/      # Shared/reusable components
│   ├── charts/      # Chart components (Plotly)
│   └── live/        # Live tracker components
├── hooks/           # Custom React hooks
├── pages/           # Page components (routes)
├── store/           # Zustand stores
├── types/           # TypeScript type definitions
├── utils/           # Utility functions
└── tests/           # Test files and setup
```

## Features

- 11 pages with lazy loading for optimal performance
- Real-time race tracking via WebSocket
- Interactive Plotly charts
- Responsive design with Tailwind CSS
- Type-safe API client with request/response interceptors
- Optimized data fetching with React Query
- Persistent user preferences with localStorage
