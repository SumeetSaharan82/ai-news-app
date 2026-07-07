import client from './client'

export const usersApi = {
  async getPreferences() {
    const res = await client.get('/users/preferences')
    return res.data
  },

  async updatePreferences(prefs) {
    const res = await client.put('/users/preferences', prefs)
    return res.data
  },

  async updateProfile({ name }) {
    const res = await client.put('/users/profile', null, { params: { name } })
    return res.data
  },
}
