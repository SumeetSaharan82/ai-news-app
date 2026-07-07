import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// Attach auth token to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('briefed_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle expired tokens globally
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('briefed_token')
      localStorage.removeItem('briefed_user')
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(err)
  }
)

export default client
