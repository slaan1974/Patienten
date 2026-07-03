import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useLockStore = defineStore('locks', () => {
  const lockStatus = ref({ locked: false })
  const lockChanges = ref(0)
  const lastLockChange = ref(null)
  let heartbeatInterval = null
  let ws = null

  function connectWebSocket(token) {
    if (ws) return
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/${token}`
    ws = new WebSocket(url)
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'lock_changed') {
          lastLockChange.value = msg
          lockChanges.value++
        }
      } catch {}
    }
    ws.onclose = () => {
      ws = null
    }
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  async function acquireLock(tableName, recordId) {
    try {
      const { data } = await api.post('/lock', { table_name: tableName, record_id: recordId })
      lockStatus.value = data
      startHeartbeat(tableName, recordId)
      return data
    } catch (err) {
      if (err.response?.status === 423) {
        const detail = err.response.data?.detail
        if (typeof detail === 'object') {
          lockStatus.value = detail
        } else {
          lockStatus.value = { locked: true, locked_by_name: 'Een andere gebruiker' }
        }
        return null
      }
      throw err
    }
  }

  async function releaseLock(tableName, recordId) {
    stopHeartbeat()
    try {
      await api.delete('/lock', { data: { table_name: tableName, record_id: recordId } })
    } catch {
    }
    lockStatus.value = { locked: false }
  }

  async function getLockStatus(tableName, recordId) {
    const { data } = await api.get(`/lock/${tableName}/${recordId}`)
    lockStatus.value = data
    return data
  }

  async function refreshLock(tableName, recordId) {
    try {
      await api.post('/lock/refresh', { table_name: tableName, record_id: recordId })
    } catch {
    }
  }

  function startHeartbeat(tableName, recordId) {
    stopHeartbeat()
    heartbeatInterval = setInterval(() => {
      refreshLock(tableName, recordId)
    }, 25000)
  }

  function releaseAllLocks() {
    stopHeartbeat()
    const token = localStorage.getItem('access_token')
    if (!token) return
    fetch('/api/lock/release-all', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      keepalive: true,
    }).catch(() => {})
    lockStatus.value = { locked: false }
  }

  function stopHeartbeat() {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  return { lockStatus, lockChanges, lastLockChange, acquireLock, releaseLock, releaseAllLocks, getLockStatus, refreshLock, stopHeartbeat, connectWebSocket, disconnectWebSocket }
})