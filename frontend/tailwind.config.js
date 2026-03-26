/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      colors: {
        f1: {
          red: '#E10600',
          black: '#121315',
          panel: 'rgba(31, 32, 34, 0.6)',
          border: 'rgba(52, 53, 55, 0.25)',
          white: '#e3e2e5',
          blue: '#0163ff',
        }
      }
    },
  },
  plugins: [],
}
