import client from './client'

function toFormData(obj) {
  const fd = new URLSearchParams()
  Object.entries(obj).forEach(([k, v]) => fd.append(k, v))
  return fd
}

export const authApi = {
  async register({ email, password, name }) {
    const body = toFormData({ username: email, password, ...(name ? { scope: name } : {}) })
    const res = await client.post('/auth/register', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return res.data
  },

  async login({ email, password }) {
    const body = toFormData({ username: email, password })
    const res = await client.post('/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return res.data
  },

  async me() {
    const res = await client.get('/auth/me')
    return res.data
  },
}
