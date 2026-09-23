tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        flash: {
          red: '#a21220',       // Deep Crimson Red
          redHover: '#850e19',  // Rich Dark Crimson Hover
          redSoft: '#fdf2f2',   // Soft crimson tint background
          dark: '#111111',      // Deep charcoal topbar
          darkSecondary: '#1e2024',
          bg: '#f2f4f7',        // Main app background
          card: '#ffffff',      // Pure white card background
          border: '#e5e7eb',    // Crisp border color
          borderDark: '#d1d5db',
          textPrimary: '#111827',
          textSecondary: '#4b5563',
          textMuted: '#6b7280'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    }
  }
};
