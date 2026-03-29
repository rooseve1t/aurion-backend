import { motion } from 'framer-motion'
import clsx from 'clsx'

type HUDModuleProps = {
  title: string
  subtitle?: string
  icon: React.ComponentType<{ className?: string }>
  children: React.ReactNode
  className?: string
}

export function HUDModule({ title, subtitle, icon: Icon, children, className = '' }: HUDModuleProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx('hud-panel flex flex-col group transition-all', className)}
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-white/[0.01]">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-[var(--amber)]/10 border border-[var(--amber)]/20">
            <Icon className="w-3.5 h-3.5 text-[var(--amber)]" />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] font-display font-bold uppercase tracking-[0.2em] text-white/90">{title}</span>
            {subtitle && (
              <span className="text-[8px] font-sans text-slate-500 uppercase tracking-widest">{subtitle}</span>
            )}
          </div>
        </div>
        <div className="flex gap-1">
          <div className="w-1 h-1 rounded-full bg-[var(--amber)]/30" />
          <div className="w-1 h-1 rounded-full bg-[var(--amber)]/30" />
        </div>
      </div>
      <div className="flex-1 p-4 overflow-hidden">
        {children}
      </div>
    </motion.div>
  )
}
