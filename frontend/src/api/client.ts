import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
})

let isRefreshing = false
let queue: Array<() => void> = []

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queue.push(() => {
          client(original).then(resolve).catch(reject)
        })
      })
    }

    original._retry = true
    isRefreshing = true

    try {
      await client.post('/auth/refresh')
      queue.forEach((cb) => cb())
      queue = []
      return client(original)
    } catch {
      queue = []
      window.location.href = '/login'
      return Promise.reject(error)
    } finally {
      isRefreshing = false
    }
  }
)

export default client
