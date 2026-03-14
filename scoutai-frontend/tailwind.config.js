/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0c',
        card: '#16161a',
        primary: {
          blue: '#00D4FF',
          green: '#00FF88',
          orange: '#FF6B35',
        },
        neon: {
          blue: '0 0 10px #00D4FF, 0 0 20px #00D4FF',
          green: '0 0 10px #00FF88, 0 0 20px #00FF88',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
