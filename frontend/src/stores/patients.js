import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const usePatientStore = defineStore('patients', () => {
  const patients = ref([])
  const loading = ref(false)
  const currentPatient = ref(null)

  async function fetchPatients() {
    loading.value = true
    try {
      const { data } = await api.get('/patients')
      patients.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchPatient(id) {
    const { data } = await api.get(`/patients/${id}`)
    currentPatient.value = data
    return data
  }

  async function createPatient(payload) {
    const { data } = await api.post('/patients', payload)
    patients.value.unshift(data)
    return data
  }

  async function updatePatient(id, payload) {
    const { data } = await api.put(`/patients/${id}`, payload)
    const idx = patients.value.findIndex((p) => p.id === id)
    if (idx !== -1) patients.value[idx] = data
    currentPatient.value = data
    return data
  }

  async function deletePatient(id) {
    await api.delete(`/patients/${id}`)
    patients.value = patients.value.filter((p) => p.id !== id)
  }

  return { patients, loading, currentPatient, fetchPatients, fetchPatient, createPatient, updatePatient, deletePatient }
})
