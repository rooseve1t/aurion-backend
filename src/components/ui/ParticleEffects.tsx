import React, { useEffect, useRef, useState } from 'react'

// Базовый particle эффект
interface Particle {
  id: number
  x: number
  y: number
  vx: number
  vy: number
  size: number
  color: string
  opacity: number
  life: number
}

interface ParticleFieldProps {
  count?: number
  speed?: number
  size?: number
  color?: string
  className?: string
  interactive?: boolean
  connectionDistance?: number
}

export function ParticleField({ 
  count = 50, 
  speed = 1, 
  size = 2, 
  color = 'var(--aurion-cyan)',
  className = '',
  interactive = false,
  connectionDistance = 150
}: ParticleFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [particles, setParticles] = useState<Particle[]>([])
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const animationRef = useRef<number>()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Initialize particles
    const initialParticles: Particle[] = Array.from({ length: count }, (_, i) => ({
      id: i,
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * speed,
      vy: (Math.random() - 0.5) * speed,
      size: Math.random() * size + 1,
      color,
      opacity: Math.random() * 0.5 + 0.3,
      life: 1
    }))

    setParticles(initialParticles)

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Update and draw particles
      initialParticles.forEach((particle, i) => {
        // Update position
        particle.x += particle.vx
        particle.y += particle.vy

        // Bounce off walls
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1

        // Mouse interaction
        if (interactive) {
          const dx = mousePos.x - particle.x
          const dy = mousePos.y - particle.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          if (distance < 100) {
            const force = (100 - distance) / 100
            particle.vx -= (dx / distance) * force * 0.5
            particle.vy -= (dy / distance) * force * 0.5
          }
        }

        // Draw connections
        initialParticles.slice(i + 1).forEach(otherParticle => {
          const dx = otherParticle.x - particle.x
          const dy = otherParticle.y - particle.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < connectionDistance) {
            ctx.beginPath()
            ctx.moveTo(particle.x, particle.y)
            ctx.lineTo(otherParticle.x, otherParticle.y)
            ctx.strokeStyle = color
            ctx.globalAlpha = (1 - distance / connectionDistance) * 0.2
            ctx.stroke()
          }
        })

        // Draw particle
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = particle.color
        ctx.globalAlpha = particle.opacity
        ctx.fill()
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [count, speed, size, color, interactive, connectionDistance, mousePos])

  useEffect(() => {
    if (!interactive) return

    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [interactive])

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 pointer-events-none ${interactive ? 'pointer-events-auto' : ''} ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}

// Floating particles effect
interface FloatingParticlesProps {
  count?: number
  shapes?: 'circle' | 'square' | 'triangle' | 'mixed'
  colors?: string[]
  speed?: number
  size?: number
  rotation?: boolean
  className?: string
}

export function FloatingParticles({ 
  count = 30, 
  shapes = 'circle',
  colors = ['var(--aurion-cyan)', 'var(--aurion-purple)', 'var(--aurion-green-dim)'],
  speed = 0.5,
  size = 4,
  rotation = true,
  className = ''
}: FloatingParticlesProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Create particles
    Array.from({ length: count }, (_, i) => {
      const particle = document.createElement('div')
      particle.className = 'aurion-floating-particle'
      
      // Random shape
      let shapeClass = ''
      switch (shapes) {
        case 'circle':
          shapeClass = 'rounded-full'
          break
        case 'square':
          shapeClass = 'rounded-sm'
          break
        case 'triangle':
          shapeClass = 'aurion-triangle'
          break
        case 'mixed':
          const shapeTypes = ['rounded-full', 'rounded-sm', 'aurion-triangle']
          shapeClass = shapeTypes[Math.floor(Math.random() * shapeTypes.length)]
          break
      }
      
      particle.className += ` ${shapeClass}`
      
      // Random properties
      const particleSize = Math.random() * size + 2
      const color = colors[Math.floor(Math.random() * colors.length)]
      const duration = (Math.random() * 20 + 10) / speed
      const delay = Math.random() * 5
      const xPos = Math.random() * 100
      const yPos = Math.random() * 100
      
      particle.style.cssText = `
        position: absolute;
        width: ${particleSize}px;
        height: ${particleSize}px;
        background: ${color};
        left: ${xPos}%;
        top: ${yPos}%;
        opacity: ${Math.random() * 0.3 + 0.1};
        animation: aurion-float-particle ${duration}s linear infinite;
        animation-delay: ${delay}s;
        pointer-events: none;
        z-index: 0;
      `
      
      if (rotation) {
        particle.style.animation += ', aurion-rotate-particle 10s linear infinite'
      }
      
      container.appendChild(particle)
    })

    return () => {
      container.innerHTML = ''
    }
  }, [count, shapes, colors, speed, size, rotation])

  return (
    <div 
      ref={containerRef} 
      className={`fixed inset-0 overflow-hidden pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}

// Matrix rain effect
interface MatrixRainProps {
  density?: number
  speed?: number
  fontSize?: number
  color?: string
  backgroundColor?: string
  className?: string
}

export function MatrixRain({ 
  density = 0.05, 
  speed = 50,
  fontSize = 14,
  color = 'var(--aurion-green-dim)',
  backgroundColor = 'rgba(0, 0, 0, 0.8)',
  className = ''
}: MatrixRainProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const columns = Math.floor(canvas.width / fontSize)
    const drops: number[] = Array(columns).fill(1)

    const draw = () => {
      ctx.fillStyle = backgroundColor
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      ctx.fillStyle = color
      ctx.font = `${fontSize}px monospace`
      
      for (let i = 0; i < drops.length; i++) {
        const text = String.fromCharCode(Math.random() * 128)
        const x = i * fontSize
        const y = drops[i] * fontSize
        
        ctx.fillText(text, x, y)
        
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0
        }
        
        drops[i]++
      }
    }

    const interval = setInterval(draw, speed)

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      clearInterval(interval)
    }
  }, [density, speed, fontSize, color, backgroundColor])

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}

// Starfield effect
interface StarfieldProps {
  count?: number
  speed?: number
  size?: number
  color?: string
  twinkle?: boolean
  className?: string
}

export function Starfield({ 
  count = 200, 
  speed = 0.5,
  size = 2,
  color = 'white',
  twinkle = true,
  className = ''
}: StarfieldProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Create stars
    Array.from({ length: count }, (_, i) => {
      const star = document.createElement('div')
      star.className = 'aurion-star'
      
      const starSize = Math.random() * size + 1
      const xPos = Math.random() * 100
      const yPos = Math.random() * 100
      const duration = (Math.random() * 3 + 2) / speed
      const delay = Math.random() * 3
      
      star.style.cssText = `
        position: absolute;
        width: ${starSize}px;
        height: ${starSize}px;
        background: ${color};
        border-radius: 50%;
        left: ${xPos}%;
        top: ${yPos}%;
        opacity: ${Math.random() * 0.8 + 0.2};
        pointer-events: none;
        z-index: 0;
      `
      
      if (twinkle) {
        star.style.animation = `aurion-twinkle ${duration}s ease-in-out infinite`
        star.style.animationDelay = `${delay}s`
      }
      
      container.appendChild(star)
    })

    return () => {
      container.innerHTML = ''
    }
  }, [count, speed, size, color, twinkle])

  return (
    <div 
      ref={containerRef} 
      className={`fixed inset-0 overflow-hidden pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}

// Geometric pattern overlay
interface GeometricOverlayProps {
  pattern?: 'hexagon' | 'triangle' | 'dots' | 'grid'
  size?: number
  color?: string
  opacity?: number
  animated?: boolean
  className?: string
}

export function GeometricOverlay({ 
  pattern = 'hexagon',
  size = 50,
  color = 'var(--aurion-cyan)',
  opacity = 0.1,
  animated = true,
  className = ''
}: GeometricOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const drawPattern = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.strokeStyle = color
      ctx.globalAlpha = opacity

      switch (pattern) {
        case 'hexagon':
          drawHexagonPattern(ctx, canvas.width, canvas.height, size)
          break
        case 'triangle':
          drawTrianglePattern(ctx, canvas.width, canvas.height, size)
          break
        case 'dots':
          drawDotPattern(ctx, canvas.width, canvas.height, size)
          break
        case 'grid':
          drawGridPattern(ctx, canvas.width, canvas.height, size)
          break
      }
    }

    drawPattern()

    if (animated) {
      const animationSpeed = 0.001
      let offset = 0
      
      const animate = () => {
        offset += animationSpeed
        ctx.save()
        ctx.translate(offset * size, offset * size)
        drawPattern()
        ctx.restore()
        requestAnimationFrame(animate)
      }
      
      animate()
    }

    return () => {
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [pattern, size, color, opacity, animated])

  const drawHexagonPattern = (ctx: CanvasRenderingContext2D, width: number, height: number, size: number) => {
    const hexHeight = size * Math.sqrt(3)
    const hexWidth = size * 2
    
    for (let row = 0; row < height / hexHeight + 1; row++) {
      for (let col = 0; col < width / (hexWidth * 0.75) + 1; col++) {
        const x = col * hexWidth * 0.75
        const y = row * hexHeight + (col % 2) * (hexHeight / 2)
        
        ctx.beginPath()
        for (let i = 0; i < 6; i++) {
          const angle = (Math.PI / 3) * i
          const xPos = x + size * Math.cos(angle)
          const yPos = y + size * Math.sin(angle)
          if (i === 0) ctx.moveTo(xPos, yPos)
          else ctx.lineTo(xPos, yPos)
        }
        ctx.closePath()
        ctx.stroke()
      }
    }
  }

  const drawTrianglePattern = (ctx: CanvasRenderingContext2D, width: number, height: number, size: number) => {
    for (let row = 0; row < height / size + 1; row++) {
      for (let col = 0; col < width / size + 1; col++) {
        const x = col * size
        const y = row * size
        
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(x + size, y)
        ctx.lineTo(x + size / 2, y + size)
        ctx.closePath()
        ctx.stroke()
      }
    }
  }

  const drawDotPattern = (ctx: CanvasRenderingContext2D, width: number, height: number, size: number) => {
    for (let row = 0; row < height / size + 1; row++) {
      for (let col = 0; col < width / size + 1; col++) {
        const x = col * size + size / 2
        const y = row * size + size / 2
        
        ctx.beginPath()
        ctx.arc(x, y, 2, 0, Math.PI * 2)
        ctx.fill()
      }
    }
  }

  const drawGridPattern = (ctx: CanvasRenderingContext2D, width: number, height: number, size: number) => {
    for (let x = 0; x < width; x += size) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }
    
    for (let y = 0; y < height; y += size) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }
  }

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}

// Aurora borealis effect
interface AuroraEffectProps {
  colors?: string[]
  intensity?: number
  speed?: number
  className?: string
}

export function AuroraEffect({ 
  colors = ['var(--aurion-cyan)', 'var(--aurion-purple)', 'var(--aurion-green-dim)'],
  intensity = 0.3,
  speed = 1,
  className = ''
}: AuroraEffectProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    let time = 0

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      colors.forEach((color, index) => {
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
        
        const offset1 = Math.sin(time * speed + index) * 0.5 + 0.5
        const offset2 = Math.cos(time * speed + index) * 0.5 + 0.5
        
        gradient.addColorStop(0, `${color}00`)
        gradient.addColorStop(offset1, `${color}${Math.floor(intensity * 255).toString(16).padStart(2, '0')}`)
        gradient.addColorStop(offset2, `${color}00`)
        
        ctx.fillStyle = gradient
        ctx.fillRect(0, 0, canvas.width, canvas.height)
      })
      
      time += 0.01
      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [colors, intensity, speed])

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  )
}


