import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
})

let isRefreshing = false
let queue: Array<() => void> = []

const inflight = new Map<string, AbortController>()

export function abortable(tag: string): { signal: AbortSignal } {
  inflight.get(tag)?.abort()
  const controller = new AbortController()
  inflight.set(tag, controller)
  return { signal: controller.signal }
}

export function isAbortError(err: unknown): boolean {
  return axios.isCancel(err) || (err as { code?: string })?.code === 'ERR_CANCELED'
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    const isAuthEndpoint = original.url?.includes('/auth/login') || original.url?.includes('/auth/refresh')

    if (error.response?.status !== 401 || original._retry || isAuthEndpoint) {
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
