module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'tax-primary': '#1f2937',
        'tax-secondary': '#059669',
        'tax-accent': '#f59e0b',
        'tax-danger': '#dc2626',
        'tax-warning': '#d97706',
        'tax-success': '#10b981',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}