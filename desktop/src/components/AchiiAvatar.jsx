import React, { useState, useEffect } from 'react'

/**
 * AchiiAvatar — "Teatterimekaaninen" 2D Achii
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

  const cx = sz / 2
  const cy = sz / 2

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

      <svg 
        width={sz} 
        height={sz} 
        viewBox={`0 0 ${sz} ${sz}`}
        className="relative z-10 transition-transform duration-300"
        style={{ transform: `scale(${breathScale})` }}
      >
        <defs>
          {/* Rusty body gradient */}
          <radialGradient id="body-rust" cx="45%" cy="40%" r="55%">
            <stop offset="0%" stopColor="#4a3728" />
            <stop offset="40%" stopColor="#3a2a1e" />
            <stop offset="80%" stopColor="#2a1e14" />
            <stop offset="100%" stopColor="#1a120c" />
          </radialGradient>

          {/* Vacuum tube inner glow */}
          <radialGradient id="tube-glow-l" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stopColor={config.eyeColor} stopOpacity={flickerOpacity} />
            <stop offset="60%" stopColor={config.eyeColor} stopOpacity={flickerOpacity * 0.4} />
            <stop offset="100%" stopColor={config.eyeColor} stopOpacity="0" />
          </radialGradient>
          <radialGradient id="tube-glow-r" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stopColor={config.eyeColor} stopOpacity={flickerOpacity} />
            <stop offset="60%" stopColor={config.eyeColor} stopOpacity={flickerOpacity * 0.4} />
            <stop offset="100%" stopColor={config.eyeColor} stopOpacity="0" />
          </radialGradient>

          {/* Shadow filter */}
          <filter id="drop-shadow">
            <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#000" floodOpacity="0.5"/>
          </filter>

          {/* Eye glow filter */}
          <filter id="eye-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* === BODY: Ruosteinen rundel === */}
        {/* Outer ring — pitted copper */}
        <circle 
          cx={cx} cy={cy} r={sz * 0.38} 
          fill="none" 
          stroke={config.bodyStroke} 
          strokeWidth="2" 
          strokeOpacity="0.3"
          strokeDasharray="4 6"
        />

        {/* Main body — rounded rect with rust texture */}
        <rect 
          x={cx - sz * 0.28} y={cy - sz * 0.30}
          width={sz * 0.56} height={sz * 0.52}
          rx="12" ry="12"
          fill="url(#body-rust)"
          stroke={config.bodyStroke}
          strokeWidth="1.5"
          filter="url(#drop-shadow)"
        />

        {/* Rivet dots — industrial detail */}
        {[-1, 1].map(dx => [-1, 1].map(dy => (
          <circle 
            key={`rivet-${dx}-${dy}`}
            cx={cx + dx * (sz * 0.22)} cy={cy + dy * (sz * 0.22)}
            r="2" fill="#607D8B" opacity="0.4"
          />
        )))}

        {/* Copper wire — antenna */}
        <line 
          x1={cx} y1={cy - sz * 0.30}
          x2={cx} y2={cy - sz * 0.40}
          stroke="#D35400" strokeWidth="1.5" strokeLinecap="round"
        />
        <circle cx={cx} cy={cy - sz * 0.41} r="2.5" fill="#F39C12" opacity={flickerOpacity} />

        {/* === EYES: Tyhjiöputket === */}
        {/* Left eye housing */}
        <circle 
          cx={cx - sz * 0.10} cy={cy - sz * 0.08}
          r={sz * 0.08}
          fill="#1a1510"
          stroke="#8B6914"
          strokeWidth="1.5"
        />
        {/* Left eye glow */}
        <circle 
          cx={cx - sz * 0.10} cy={cy - sz * 0.08}
          r={sz * 0.06}
          fill="url(#tube-glow-l)"
          filter="url(#eye-glow)"
        />
        {/* Left pupil */}
        <circle 
          cx={cx - sz * 0.10} cy={cy - sz * 0.09}
          r={sz * 0.02}
          fill={config.eyeColor}
          opacity={flickerOpacity}
        />

        {/* Right eye housing */}
        <circle 
          cx={cx + sz * 0.10} cy={cy - sz * 0.08}
          r={sz * 0.08}
          fill="#1a1510"
          stroke="#8B6914"
          strokeWidth="1.5"
        />
        {/* Right eye glow */}
        <circle 
          cx={cx + sz * 0.10} cy={cy - sz * 0.08}
          r={sz * 0.06}
          fill="url(#tube-glow-r)"
          filter="url(#eye-glow)"
        />
        {/* Right pupil */}
        <circle 
          cx={cx + sz * 0.10} cy={cy - sz * 0.09}
          r={sz * 0.02}
          fill={config.eyeColor}
          opacity={flickerOpacity}
        />

        {/* === MOUTH: Wrench slit === */}
        <line 
          x1={cx - sz * 0.06} y1={cy + sz * 0.06}
          x2={cx + sz * 0.06} y2={cy + sz * 0.06}
          stroke="#607D8B" strokeWidth="1.5" strokeLinecap="round"
        />
        {/* Small wrench icon below mouth */}
        <g transform={`translate(${cx}, ${cy + sz * 0.14})`} opacity="0.5">
          <polygon 
            points="-4,-2 -2,-4 2,-4 4,-2 2,0 -2,0" 
            fill="none" 
            stroke="#D35400" 
            strokeWidth="1"
          />
          <line x1="0" y1="0" x2="0" y2="8" stroke="#D35400" strokeWidth="1" strokeLinecap="round"/>
        </g>

        {/* === FEETS: Kuparijohdot === */}
        <line 
          x1={cx - sz * 0.12} y1={cy + sz * 0.22}
          x2={cx - sz * 0.15} y2={cy + sz * 0.35}
          stroke="#D35400" strokeWidth="1.5" strokeLinecap="round" opacity="0.4"
        />
        <line 
          x1={cx + sz * 0.12} y1={cy + sz * 0.22}
          x2={cx + sz * 0.15} y2={cy + sz * 0.35}
          stroke="#D35400" strokeWidth="1.5" strokeLinecap="round" opacity="0.4"
        />
      </svg>

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
