import { useEffect, useRef } from 'react'
import styles from './CoreOrb.module.css'

interface Props {
  active?: boolean
  size?: number
}

export function CoreOrb({ active = true, size = 80 }: Props) {
  const orbRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!active || !orbRef.current) return
    let frame: number
    let angle = 0
    const animate = () => {
      angle += 0.5
      if (orbRef.current) {
        orbRef.current.style.transform = `rotate(${angle}deg)`
      }
      frame = requestAnimationFrame(animate)
    }
    frame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(frame)
  }, [active])

  return (
    <div
      className={`${styles.orb} ${active ? styles.active : ''}`}
      style={{ width: size, height: size }}
    >
      <div className={styles.ring} ref={orbRef} />
      <div className={styles.core} />
      <div className={styles.glow} />
    </div>
  )
}
