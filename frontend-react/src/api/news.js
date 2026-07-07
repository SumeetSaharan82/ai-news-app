import client from './client'

export const newsApi = {
  async getPersonalized({ limit = 30 } = {}) {
    const res = await client.get('/news/personalized', { params: { limit } })
    return res.data
  },

  async getRss({ category, region, limit = 20 } = {}) {
    const params = { limit }
    if (category) params.category = category
    if (region) params.region = region
    const res = await client.get('/news/rss', { params })
    return res.data
  },

  async getNews({ category, region, page = 1, per_page = 20, search, sort_by = 'recent' } = {}) {
    const params = { page, per_page, sort_by }
    if (category) params.category = category
    if (region) params.region = region
    if (search) params.search = search
    const res = await client.get('/news', { params })
    return res.data
  },

  async getCategories() {
    const res = await client.get('/categories')
    return res.data
  },

  async getRegions() {
    const res = await client.get('/regions')
    return res.data
  },
}
