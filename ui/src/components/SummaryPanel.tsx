import { useRef, useState, useEffect } from 'react'
import type { SummaryData, DeveloperProfile } from '../types'
import './SummaryPanel.css'

interface Props {
  summary: SummaryData
  developerProfile: DeveloperProfile | null
}

const SECTIONS = [
  { id: 'what-it-does', label: 'What it does' },
  { id: 'start-here', label: 'Start here' },
  { id: 'stable', label: 'Stable' },
  { id: 'hotspots', label: 'Hotspots' },
  { id: 'clusters', label: 'Clusters' },
] as const

type SectionId = (typeof SECTIONS)[number]['id']

export default function SummaryPanel({ summary, developerProfile }: Props) {
  const [activeSection, setActiveSection] = useState<SectionId>('what-it-does')
  const scrollRef = useRef<HTMLDivElement>(null)
  const sectionRefs = useRef<Partial<Record<SectionId, HTMLElement>>>({})

  useEffect(() => {
    const container = scrollRef.current
    if (!container) return

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id as SectionId)
            break
          }
        }
      },
      { root: container, threshold: 0.25 }
    )

    Object.values(sectionRefs.current).forEach((el) => {
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  function scrollTo(id: SectionId) {
    sectionRefs.current[id]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="summary-panel">
      <nav className="summary-nav">
        <div className="summary-nav__repo">{summary.repo_name}</div>
        {SECTIONS.map(({ id, label }) => (
          <button
            key={id}
            className={`summary-nav__item ${activeSection === id ? 'summary-nav__item--active' : ''}`}
            onClick={() => scrollTo(id)}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="summary-content" ref={scrollRef}>
        {developerProfile && (
          <div className="summary-greeting">
            Welcome, {developerProfile.name}. Here's what you need to know about{' '}
            <strong>{summary.repo_name}</strong>.
          </div>
        )}

        <section id="what-it-does" ref={(el) => { if (el) sectionRefs.current['what-it-does'] = el }}>
          <h2>What it does</h2>
          <p>{summary.what_it_does}</p>
        </section>

        <section id="start-here" ref={(el) => { if (el) sectionRefs.current['start-here'] = el }}>
          <h2>Start here</h2>
          <ol className="read-first-list">
            {summary.read_first.map((item) => (
              <li key={item.path}>
                <code>{item.path}</code>
                <span>{item.reason}</span>
              </li>
            ))}
          </ol>
        </section>

        <section id="stable" ref={(el) => { if (el) sectionRefs.current['stable'] = el }}>
          <h2>Stable</h2>
          <ul className="file-list">
            {summary.stable.map((item) => (
              <li key={item.path}>
                <code>{item.path}</code>
                <span>{item.note}</span>
              </li>
            ))}
          </ul>
        </section>

        <section id="hotspots" ref={(el) => { if (el) sectionRefs.current['hotspots'] = el }}>
          <h2>Hotspots</h2>
          {summary.hotspots.length === 0 ? (
            <p className="summary-empty">No active hotspots detected. The codebase appears stable.</p>
          ) : (
            <ul className="file-list file-list--hotspot">
              {summary.hotspots.map((item) => (
                <li key={item.path}>
                  <code>{item.path}</code>
                  <span>{item.note}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section id="clusters" ref={(el) => { if (el) sectionRefs.current['clusters'] = el }}>
          <h2>Clusters</h2>
          <div className="cluster-list">
            {summary.clusters.map((cluster) => (
              <div key={cluster.id} className="cluster-card">
                <div className="cluster-card__label">Cluster {cluster.id}</div>
                <p>{cluster.summary}</p>
                <ul className="cluster-card__files">
                  {cluster.files.map((f) => (
                    <li key={f}>
                      <code>{f}</code>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
