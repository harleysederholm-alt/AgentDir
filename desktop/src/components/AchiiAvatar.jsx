import React, { useState, useEffect } from 'react'

/**
 * AchiiAvatar — "Teatterimekaaninen" 2D Achii -> Vaihdettu 3D-malliin
 * 
 * Brändikirja v4.6: Ruosteinen runko, hehkuvat tyhjiöputkisilmät,
 * kuparijohdot, Theater Black -lavalla spotlight-efektillä.
 * 
 * Tilat: normal, thinking, happy, warning, focused, error, idle
 */

const STATE_CONFIG = {
  normal:   { eyeColor: '#F39C12', bodyStroke: '#D35400', label: 'AWAKE',    eyePulse: false },
  thinking: { eyeColor: '#F39C12', bodyStroke: '#F39C12', label: 'THINKING', eyePulse: true },
  happy:    { eyeColor: '#F5B041', bodyStroke: '#D35400', label: 'HAPPY',    eyePulse: false },
  warning:  { eyeColor: '#E74C3C', bodyStroke: '#C0392B', label: 'NEEDY',    eyePulse: true },
  focused:  { eyeColor: '#F39C12', bodyStroke: '#D35400', label: 'FOCUSED',  eyePulse: false },
  error:    { eyeColor: '#E74C3C', bodyStroke: '#C0392B', label: 'ERROR',    eyePulse: true },
  idle:     { eyeColor: '#607D8B', bodyStroke: '#455A64', label: 'IDLE',     eyePulse: false },
}

export default function AchiiAvatar({ achiiState = 'normal', size = 'large' }) {
  const [breathScale, setBreathScale] = useState(1)
  const [flickerOpacity, setFlickerOpacity] = useState(0.85)
  const config = STATE_CONFIG[achiiState] || STATE_CONFIG.normal
  const sz = size === 'small' ? 120 : 200

  // Breathing + vacuum tube flicker
  useEffect(() => {
    let frame
    let t = 0
    const animate = () => {
      t += 0.015
      const speed = config.eyePulse ? 3.5 : 1.2
      setBreathScale(1 + Math.sin(t * speed) * (config.eyePulse ? 0.04 : 0.02))
      // Tyhjiöputki-flicker
      setFlickerOpacity(0.8 + Math.sin(t * 7) * 0.08 + Math.sin(t * 13) * 0.05)
      frame = requestAnimationFrame(animate)
    }
    frame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(frame)
  }, [config.eyePulse])

  return (
    <div className="flex flex-col items-center justify-center gap-3 relative">
      {/* Spotlight from above */}
      <div 
        className="absolute rounded-full blur-[80px] pointer-events-none"
        style={{
          width: sz * 1.8,
          height: sz * 1.2,
          top: -sz * 0.4,
          background: `radial-gradient(ellipse, rgba(243,156,18,${config.eyePulse ? 0.12 : 0.06}), transparent 70%)`,
        }}
      />

      {/* === 3D ACHII HEAD (Clean PNG, no background) === */}
      <div 
        className="relative rounded-full flex items-center justify-center transition-transform duration-300 z-10"
        style={{ 
          width: sz, 
          height: sz,
          transform: `scale(${breathScale})`,
          background: 'transparent',
        }}
      >
        {/* Hehkuva kehä pään takana */}
        <div
          className="absolute inset-0 rounded-full pointer-events-none"
          style={{
            boxShadow: `0 0 ${config.eyePulse ? '30px' : '15px'} ${config.eyeColor}30, inset 0 0 ${config.eyePulse ? '20px' : '10px'} ${config.eyeColor}10`,
            border: `1.5px solid ${config.bodyStroke}50`,
          }}
        />
        {/* Puhdas taustaton robotin pää */}
        <img 
          src="/achii_head_clean.png" 
          alt="Achii 3D Avatar" 
          className="w-full h-full object-contain"
          style={{
            filter: `drop-shadow(0 0 12px ${config.eyeColor}40)`,
          }}
        />
        
        {/* Silmien "Tyhjiöputki" -hehku overlay */}
        <div 
          className="absolute inset-0 pointer-events-none mix-blend-screen rounded-full"
          style={{
            background: `radial-gradient(circle at 50% 48%, ${config.eyeColor}${Math.floor(flickerOpacity * 40).toString(16).padStart(2, '0')}, transparent 65%)`
          }}
        />
      </div>

      {/* State label — CLI-tyyli */}
      <div 
        className="relative z-10 px-3 py-1 rounded text-[10px] font-mono font-bold tracking-[0.25em] uppercase transition-all duration-500"
        style={{ 
          color: config.eyeColor, 
          borderColor: config.bodyStroke,
          border: `1px solid ${config.bodyStroke}40`,
          backgroundColor: `${config.eyeColor}08`,
          textShadow: `0 0 8px ${config.eyeColor}40`,
        }}
      >
        ● {config.label}
      </div>
    </div>
  )
}
