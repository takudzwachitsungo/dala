
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
  './index.html',
  './src/**/*.{js,ts,jsx,tsx}'
],
  theme: {
    extend: {
      colors: {
        background: '#FAFAF9', // Soft off-white
        primary: '#78716C',    // Warm gray
        secondary: '#A8A29E',  // Lighter warm gray
        subtle: '#D6D3D1',     // Very light gray
        divider: '#E7E5E4',    // Thin divider color
        sage: {
          DEFAULT: '#A3B18A',
          hover: '#8F9E77',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      lineHeight: {
        relaxed: '1.8',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      }
    },
  },
  plugins: [],
}
