import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuditStore = defineStore('audit', () => {
  const logs = ref([])
  const currentLog = ref(null)

  async function fetchLogs(params = {}) {
    const { data } = await api.get('/audit', { params })
    logs.value = data
  }

  async function fetchLog(id) {
    const { data } = await api.get(`/audit/${id}`)
    currentLog.value = data
    return data
  }

  return { logs, currentLog, fetchLogs, fetchLog }
})
