const warmNeutral = {
  50: '#faf8f2', 100: '#f3efe5', 200: '#e9e3d5',
  300: '#d8cebb', 400: '#a99b83', 500: '#756c60',
  600: '#655b4d', 700: '#514537', 800: '#44372c',
  900: '#352a23', 950: '#251d18'
}

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Warm neutrals unify cards, tables and typography across the console.
        white: '#fffefa',
        gray: warmNeutral,
        slate: warmNeutral,
        accent: warmNeutral,
        brand: { yellow: '#f4d438', ink: '#352a23', canvas: '#faf8f2' },
        // Dark gold text remains readable on cream; bright yellow is an accent.
        primary: {
          50: '#fff9e6', 100: '#fff1bc', 200: '#f9e58b',
          300: '#f4d438', 400: '#dfbf32', 500: '#8c6814',
          600: '#795710', 700: '#65460f', 800: '#513914',
          900: '#402e16', 950: '#2a2114'
        },
        // Explicit dark-mode preference uses warm cocoa, not blue-black.
        dark: {
          50: '#faf8f2', 100: '#f3efe5', 200: '#e9e3d5',
          300: '#d8cebb', 400: '#b9ad98', 500: '#958771',
          600: '#726452', 700: '#514537', 800: '#3a3128',
          900: '#2c251f', 950: '#211c17'
        }
      },
      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'PingFang SC',
          'Hiragino Sans GB',
          'Microsoft YaHei',
          'sans-serif'
        ],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0, 0, 0, 0.08)',
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.06)',
        glow: '0 0 20px rgba(172, 133, 33, 0.25)',
        'glow-lg': '0 0 40px rgba(172, 133, 33, 0.35)',
        card: '0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 40px rgba(0, 0, 0, 0.08)',
        'inner-glow': 'inset 0 1px 0 rgba(255, 255, 255, 0.1)'
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-primary': 'linear-gradient(135deg, #8c6814 0%, #795710 100%)',
        'gradient-dark': 'linear-gradient(135deg, #3a3128 0%, #2c251f 100%)',
        'gradient-glass':
          'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        'mesh-gradient':
          'radial-gradient(at 40% 20%, rgba(172, 133, 33, 0.04) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(244, 212, 56, 0.05) 0px, transparent 50%), radial-gradient(at 0% 50%, rgba(172, 133, 33, 0.03) 0px, transparent 50%)'
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        shimmer: 'shimmer 2s linear infinite',
        glow: 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' }
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' }
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' }
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(172, 133, 33, 0.25)' },
          '100%': { boxShadow: '0 0 30px rgba(172, 133, 33, 0.4)' }
        }
      },
      backdropBlur: {
        xs: '2px'
      },
      borderRadius: {
        '4xl': '2rem'
      }
    }
  },
  plugins: []
}
