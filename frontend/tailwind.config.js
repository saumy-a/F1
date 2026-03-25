/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        f1: {
          red: '#E10600',
          black: '#15151E',
          white: '#FFFFFF',
          gray: {
            100: '#F7F4F1',
            200: '#E8E8E8',
            300: '#D0D0D2',
            400: '#939598',
            500: '#58595B',
          }
        }
      }
    },
  },
  plugins: [],
}
