/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        emerald: {
          50: '#e1f2e5',
          100: '#c3e5cb',
          200: '#a4d8b0',
          300: '#86c992',
          400: '#68bc75',
          500: '#54a96b',  // #05402C
          600: '#48855c',
          700: '#3c704d',
          800: '#315c40',
          900: '#274a33',
        }
      }
    },
  },
  plugins: [],
}
