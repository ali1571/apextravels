module.exports = {
  content: [
    "./core/templates/**/*.html",
    "./core/static/**/*.js",
    // Add your template paths here
  ],
  plugins: [
    require('daisyui'),  // DaisyUI goes here!
  ],
  daisyui: {
    themes: ["light", "dark", "cupcake"], // Optional: configure themes
  },
}

daisyui: {
    themes: [
      {
        luxury_blue: {
          "primary": "#3b82f6",     // The vibrant blue
          "secondary": "#1e3a8a",
          "accent": "#60a5fa",
          "neutral": "#1f2937",
          "base-100": "#ffffff",
          "info": "#3abff8",
          "success": "#36d399",
          "warning": "#fbbd23",
          "error": "#f87272",
        },
      },
    ],
},