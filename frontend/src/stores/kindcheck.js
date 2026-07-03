import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useKindcheckStore = defineStore('kindcheck', () => {
  const currentForm = ref(null)
  const allStatus = ref([])
  const terminologie = ref({})

  async function fetchTerminologie() {
    const { data } = await api.get('/kindcheck/terminologie')
    terminologie.value = data
    return data
  }

  async function fetchForm(patientId) {
    const { data } = await api.get(`/kindcheck/${patientId}`)
    currentForm.value = data
    return data
  }

  async function saveForm(patientId, payload) {
    const clean = { patient_id: patientId }
    const FORM_FIELDS = ['datum', 'herkomst', 'herkomst_anders', 'kleinstiefpleeg', 'opkomst', 'opmerking_gedeelde_zorg', 'opmerking_alleen_zorg', 'kinderen']
    for (const key of FORM_FIELDS) {
      if (key in payload) clean[key] = payload[key]
    }
    const { data } = await api.post(`/kindcheck/${patientId}`, clean)
    currentForm.value = data
    return data
  }

  async function updateForm(formId, payload) {
    const { data } = await api.put(`/kindcheck/form/${formId}`, payload)
    currentForm.value = data
    return data
  }

  async function deleteForm(formId) {
    await api.delete(`/kindcheck/form/${formId}`)
    currentForm.value = null
  }

  async function fetchAllStatus() {
    const { data } = await api.get('/kindcheck/status/all')
    allStatus.value = data
    return data
  }

  return { currentForm, allStatus, terminologie, fetchForm, saveForm, updateForm, deleteForm, fetchAllStatus, fetchTerminologie }
})
