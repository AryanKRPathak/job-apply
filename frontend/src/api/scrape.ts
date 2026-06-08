import client from './client'

export const scrapeNow = (portals?: string[]): Promise<{ task_id: string; status: string }> =>
  client.post('/scrape/now', null, { params: portals ? { portals } : {} }).then((r) => r.data)

export const getScrapeStatus = (task_id: string) =>
  client.get('/scrape/status', { params: { task_id } }).then((r) => r.data)

export const getScrapeLogs = () =>
  client.get('/scrape/logs').then((r) => r.data)
