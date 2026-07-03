export interface ReadFirst {
  path: string
  reason: string
}

export interface StableFile {
  path: string
  note: string
}

export interface Hotspot {
  path: string
  note: string
}

export interface SummaryCluster {
  id: number
  summary: string
  files: string[]
  coupling_pairs: [string, string][]
}

export interface SummaryData {
  repo_name: string
  generated_at: string
  what_it_does: string
  read_first: ReadFirst[]
  stable: StableFile[]
  hotspots: Hotspot[]
  clusters: SummaryCluster[]
}

export interface Rule {
  id: string
  rule: string
  why: string
  example: string
}

export interface RulesCluster {
  name: string
  context: string
  golden_file: string
  rules: Rule[]
}

export interface RulesData {
  clusters: RulesCluster[]
}

export interface DeveloperProfile {
  name: string
  role?: string
  focusArea?: string
}
