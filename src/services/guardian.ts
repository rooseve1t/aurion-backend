import { api } from './api'

interface GuardianScanResponse {
  scanned_hosts: number
  report: Array<{
    host: string
    open_ports: number[]
    risks: string[]
    score: number
  }>
  recommendations: string[]
}

interface RouterAuditResponse {
  checks: Array<{
    item: string
    status: 'ok' | 'warning'
    message: string
  }>
}

export const guardianService = {
  async scan(hosts: string[]): Promise<GuardianScanResponse> {
    const { data } = await api.post<GuardianScanResponse>('/guardian/scan', { hosts })
    return data
  },

  async routerAudit(): Promise<RouterAuditResponse> {
    const { data } = await api.get<RouterAuditResponse>('/guardian/router-audit')
    return data
  },
}
