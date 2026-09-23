// Memastikan variabel tailwind.config langsung dikenali oleh CDN Tailwind
tailwind.config = {
  theme: {
    extend: {
      colors: {
        flash: {
          red: '#a21220',          // Warna Crimson Red Utama (Header)
          redHover: '#850e19',     // Red Hover State
          redSoft: '#fdf2f2',      // Soft Red Background untuk kartu risiko
          dark: '#111111',         // Top Charcoal Status Bar & Footer
          darkSecondary: '#1e2024',
          bg: '#f2f4f7',           // Background Utama Aplikasi
          card: '#ffffff',         // Background Card Match
          border: '#e5e7eb',       // Border Soft
          borderDark: '#d1d5db',   // Border Medium
          textPrimary: '#111827',  // Warna Teks Utama
          textSecondary: '#4b5563',// Warna Teks Sekunder
          textMuted: '#6b7280'     // Warna Teks Muted
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    }
  }
};
