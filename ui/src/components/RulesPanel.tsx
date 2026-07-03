import { useState } from 'react'
import type { RulesData } from '../types'
import './RulesPanel.css'

interface Props {
  rules: RulesData
}

export default function RulesPanel({ rules }: Props) {
  const [expandedCluster, setExpandedCluster] = useState<string | null>(null)

  function toggle(name: string) {
    setExpandedCluster((prev) => (prev === name ? null : name))
  }

  return (
    <div className="rules-panel">
      <div className="rules-panel__header">
        <h1>Rules</h1>
      </div>

      <div className="rules-content">
        {rules.clusters.map((cluster) => (
          <div key={cluster.name} className="rules-cluster">
            <button
              className={`rules-cluster__trigger ${expandedCluster === cluster.name ? 'rules-cluster__trigger--open' : ''}`}
              onClick={() => toggle(cluster.name)}
            >
              <span className="rules-cluster__name">{cluster.name}</span>
              <span className="rules-cluster__count">{cluster.rules.length} rules</span>
            </button>

            {expandedCluster === cluster.name && (
              <div className="rules-cluster__body">
                <p className="rules-cluster__context">{cluster.context}</p>
                <div className="rules-cluster__golden">
                  golden file: <code>{cluster.golden_file}</code>
                </div>
                <ul className="rule-list">
                  {cluster.rules.map((rule) => (
                    <li key={rule.id} className="rule-item">
                      <div className="rule-item__header">
                        <code className="rule-item__id">{rule.id}</code>
                        <p className="rule-item__rule">{rule.rule}</p>
                      </div>
                      <p className="rule-item__why">{rule.why}</p>
                      <pre><code>{rule.example}</code></pre>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
