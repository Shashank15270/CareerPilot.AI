/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        // Small phones (iPhone SE / Mini) need a step below Tailwind's sm:640.
        xs: '400px',
      },
      colors: {
        primary: "#704F38",     // Deep Hazelnut
        secondary: "#1B2A4A",   // Deep Sapphire
        accent: "#BD5A32",      // Burnt Copper
        background: "#FAF7F2",  // Warm Ivory
        card: "#1C1C1E",        // Soft Charcoal
        text: "#1C1A17",        // Warm Dark Text
        surface: "#F4F0E6",     // Soft Cream
        muted: "#78716C",       // Warm Slate
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
