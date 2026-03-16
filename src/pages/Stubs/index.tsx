import { Construction } from 'lucide-react'

interface StubPageProps {
  title: string
  description?: string
}

export function StubPage({ title, description }: StubPageProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 text-center p-8">
      <Construction size={48} className="text-white/15" />
      <div>
        <div className="font-bold text-sm tracking-widest text-white/40">{title.toUpperCase()}</div>
        <div className="text-xs text-white/20 mt-1">{description ?? 'Модуль в разработке'}</div>
      </div>
      <div className="text-[10px] text-white/10 tracking-widest border border-white/10 px-4 py-2 rounded">
        COMING SOON
      </div>
    </div>
  )
}
