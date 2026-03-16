interface CoreOrbProps {
  size?: number
  active?: boolean
  pulse?: boolean
  color?: string
}

export function CoreOrb({ size = 80, active = true, pulse = true, color = '#00e5ff' }: CoreOrbProps) {
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {pulse && active && (
        <>
          <div
            className="absolute rounded-full animate-ping"
            style={{
              width: size * 0.85, height: size * 0.85,
              background: `radial-gradient(circle, ${color}20, transparent)`,
              border: `1px solid ${color}40`,
            }}
          />
          <div
            className="absolute rounded-full animate-pulse"
            style={{
              width: size * 0.65, height: size * 0.65,
              background: `radial-gradient(circle, ${color}15, transparent)`,
            }}
          />
        </>
      )}
      <div
        className="relative rounded-full flex items-center justify-center"
        style={{
          width: size * 0.5, height: size * 0.5,
          background: `radial-gradient(circle at 35% 35%, ${color}80, ${color}20)`,
          boxShadow: active ? `0 0 ${size * 0.3}px ${color}60, inset 0 0 ${size * 0.15}px ${color}40` : 'none',
          border: `1px solid ${color}60`,
        }}
      />
    </div>
  )
}
