import { Link } from 'react-router-dom'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import styles from './LandingPage.module.css'

export function LandingPage() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <span className={styles.brandMark}>AURION</span>
          <span className={styles.brandSub}>QUANTUM AI OS</span>
        </div>
        <nav className={styles.nav}>
          <a href="#mission">Миссия</a>
          <a href="#metrics">Метрики</a>
          <a href="#voice">Голос</a>
          <a href="#tech">Технологии</a>
        </nav>
        <div className={styles.headerActions}>
          <Link to="/auth/login" className={styles.ghostBtn}>Войти</Link>
          <Link to="/boot" className={styles.primaryBtn}>Запустить систему</Link>
        </div>
      </header>

      <main>
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <div className={styles.heroKicker}>NON-TOUCH CONTROL</div>
            <h1 className={styles.heroTitle}>
              Квантовый интеллект,
              <span> который держит систему в идеальном порядке</span>
            </h1>
            <p className={styles.heroBody}>
              Aurion OS — это автономный контур управления, где голос, метрики и миссии
              синхронизированы в едином поле. Без визуальных сдвигов, без шума, без скрытых ошибок.
            </p>
            <div className={styles.heroActions}>
              <Link to="/boot" className={styles.primaryBtn}>Войти в контур</Link>
              <Link to="/auth/login" className={styles.ghostBtn}>Перейти к приложению</Link>
            </div>
            <div className={styles.heroMeta}>
              <div>
                <span className={styles.metaLabel}>Состояние</span>
                <span className={styles.metaValue}>ONLINE</span>
              </div>
              <div>
                <span className={styles.metaLabel}>Режим</span>
                <span className={styles.metaValue}>AUTONOMOUS</span>
              </div>
              <div>
                <span className={styles.metaLabel}>Протокол</span>
                <span className={styles.metaValue}>JARVIS</span>
              </div>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <div className={styles.orbFrame}>
              <CoreOrb size={220} active />
            </div>
            <div className={styles.orbCaption}>
              Центральное ядро автономности
            </div>
          </div>
        </section>

        <section id="mission" className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Mission</span>
            <h2 className={styles.sectionTitle}>Технологический прорыв в управлении интеллектом</h2>
          </div>
          <p className={styles.sectionBody}>
            Мы строим систему, которая ощущается как Джарвис: точная, спокойная,
            предвосхищающая действия. Всё, что делает Aurion OS, — это чёткая инженерия
            и выверенный визуал, где каждое движение имеет смысл.
          </p>
        </section>

        <section id="metrics" className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>System Metrics</span>
            <h2 className={styles.sectionTitle}>Контроль состояния в одном взгляде</h2>
          </div>
          <div className={styles.metricsGrid}>
            <div>
              <span className={styles.metricLabel}>Активных контуров</span>
              <span className={styles.metricValue}>12</span>
            </div>
            <div>
              <span className={styles.metricLabel}>Потоков миссий</span>
              <span className={styles.metricValue}>8</span>
            </div>
            <div>
              <span className={styles.metricLabel}>Стабильность</span>
              <span className={styles.metricValue}>99.9%</span>
            </div>
            <div>
              <span className={styles.metricLabel}>Голосовой канал</span>
              <span className={styles.metricValue}>READY</span>
            </div>
          </div>
        </section>

        <section id="voice" className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Voice Channel</span>
            <h2 className={styles.sectionTitle}>Голос как единственный интерфейс</h2>
          </div>
          <p className={styles.sectionBody}>
            Aurora-диалог работает в реальном времени: слушает, анализирует, реагирует.
            Больше не нужно держать в голове десятки окон — вы управляете системой голосом.
          </p>
          <div className={styles.voicePanel}>
            <div>
              <div className={styles.voiceTitle}>Aurion Listening</div>
              <div className={styles.voiceStatus}>Ожидаю команду оператора</div>
            </div>
            <Link to="/boot" className={styles.primaryBtn}>Активировать канал</Link>
          </div>
        </section>

        <section id="tech" className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Architecture</span>
            <h2 className={styles.sectionTitle}>Квантовая архитектура, собранная в единый контур</h2>
          </div>
          <p className={styles.sectionBody}>
            В основе — автономные агенты, квантовые вычисления и нейросетевые
            слои, синхронизированные в одно стабильное поле. Система остаётся
            стабильной независимо от нагрузки и сценария.
          </p>
        </section>
      </main>
    </div>
  )
}
