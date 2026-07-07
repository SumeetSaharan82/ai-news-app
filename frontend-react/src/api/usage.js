import client from './client'

export const usageApi = {
  async getStatus() {
    const res = await client.get('/usage/status')
    return res.data
  },

  async recordRead() {
    try {
      const res = await client.post('/usage/record-read')
      return { ok: true, data: res.data }
    } catch (err) {
      if (err.response?.status === 402) {
        return { ok: false, limitExceeded: true, data: err.response.data.detail }
      }
      // Network errors — fail silently, don't block reading
      return { ok: true, data: null }
    }
  },
}
