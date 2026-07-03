import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useDsm5Store = defineStore('dsm5', () => {
  const currentForm = ref(null)
  const allStatus = ref([])

  async function fetchForm(patientId) {
    const { data } = await api.get(`/dsm5/${patientId}`)
    currentForm.value = data
    return data
  }

  const FORM_FIELDS = ['status', 'criteria_a', 'criteria_b', 'criteria_c', 'criteria_d', 'criteria_e', 'dimensies', 'conclusie']

  async function saveForm(patientId, payload) {
    const clean = { patient_id: patientId }
    for (const key of FORM_FIELDS) {
      if (key in payload) clean[key] = payload[key]
    }
    const { data } = await api.post(`/dsm5/${patientId}`, clean)
    currentForm.value = data
    return data
  }

  async function updateForm(formId, payload) {
    const { data } = await api.put(`/dsm5/form/${formId}`, payload)
    currentForm.value = data
    return data
  }

  async function deleteForm(formId) {
    await api.delete(`/dsm5/form/${formId}`)
    currentForm.value = null
  }

  async function fetchAllStatus() {
    const { data } = await api.get('/dsm5/status/all')
    allStatus.value = data
    return data
  }

  return { currentForm, allStatus, fetchForm, saveForm, updateForm, deleteForm, fetchAllStatus }
})
