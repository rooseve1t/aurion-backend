import { useEffect, useState } from 'react'
import { MessagesSquare, Send } from 'lucide-react'
import { socialService } from '@/services/social'
import { useToast } from '@/hooks/useToast'
import { timeAgo } from '@/utils'
import type { SocialPost } from '@/types'
import styles from './Workspace.module.css'

export function SocialPage() {
  const [feed, setFeed] = useState<SocialPost[]>([])
  const [content, setContent] = useState('')
  const [mood, setMood] = useState<SocialPost['mood']>('insight')
  const toast = useToast()

  const load = async () => {
    try {
      setFeed(await socialService.list())
    } catch {
      toast.error('Не удалось загрузить social-ленту')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const publish = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!content.trim()) return
    try {
      const post = await socialService.create(content.trim(), mood)
      setFeed((current) => [post, ...current])
      setContent('')
      setMood('insight')
      toast.success('Пост опубликован')
    } catch {
      toast.error('Не удалось опубликовать запись')
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleBlock}>
          <MessagesSquare size={20} color="var(--cyan)" />
          <div>
            <div className={styles.title}>SOCIAL PULSE</div>
            <div className={styles.subtitle}>Лента статусов, founder-заметок и командных сигналов по продукту</div>
          </div>
        </div>
      </div>

      <form className={styles.card} onSubmit={publish}>
        <div className={styles.sectionTitle}>Новая запись</div>
        <textarea
          className={styles.textArea}
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Поделись сигналом для команды, заметкой или обновлением статуса..."
        />
        <div className={styles.actions}>
          <select className="input" value={mood} onChange={(event) => setMood(event.target.value as SocialPost['mood'])}>
            <option value="insight">Insight</option>
            <option value="focus">Focus</option>
            <option value="warning">Warning</option>
            <option value="calm">Calm</option>
          </select>
          <button type="submit" className="btn btn-cyan" disabled={!content.trim()}>
            <Send size={14} />
            ОПУБЛИКОВАТЬ
          </button>
        </div>
      </form>

      <section className={styles.card}>
        <div className={styles.sectionTitle}>Лента</div>
        <div className={styles.list}>
          {feed.map((post) => (
            <div key={post.id} className={styles.item}>
              <div className={styles.itemRow}>
                <div className={styles.itemTitle}>{post.author_name}</div>
                <div className={styles.badge}>{post.mood}</div>
              </div>
              <div className={styles.itemMeta}>{post.content}</div>
              <div className={styles.badgeRow}>
                <span className={styles.badge}>{post.source}</span>
                <span className={styles.badge}>{timeAgo(post.created_at)}</span>
                {Object.entries(post.reactions).map(([name, count]) => (
                  <span key={name} className={styles.badge}>{name} {count}</span>
                ))}
              </div>
            </div>
          ))}
          {feed.length === 0 && <div className={styles.empty}>Пока нет записей</div>}
        </div>
      </section>
    </div>
  )
}
