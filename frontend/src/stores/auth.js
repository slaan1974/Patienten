import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import { useLockStore } from './locks'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const { data } = await api.post('/auth/login', { username, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    token.value = data.access_token
    const lockStore = useLockStore()
    lockStore.connectWebSocket(data.access_token)
    await fetchUser()
  }

  async function fetchUser() {
    try {
      const { data } = await api.get('/patients')
      user.value = { username: 'Gebruiker' }
    } catch {
      logout()
    }
  }

  function logout() {
    const lockStore = useLockStore()
    lockStore.disconnectWebSocket()
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    token.value = null
    user.value = null
  }

  if (token.value) {
    const lockStore = useLockStore()
    lockStore.connectWebSocket(token.value)
  }

  return { user, token, isLoggedIn, login, logout, fetchUser }
})
