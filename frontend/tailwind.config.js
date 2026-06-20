/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b1220",
        panel: "#121a2b",
        panel2: "#1a2438",
        border: "#243047",
        accent: "#22d3ee",
        accent2: "#34d399",
        warn: "#fbbf24",
        danger: "#f87171",
      },
    },
  },
  plugins: [],
};
