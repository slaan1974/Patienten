<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { usePatientStore } from '../stores/patients'
import { useDsm5Store } from '../stores/dsm5'
import { useLockStore } from '../stores/locks'
import ReadOnlyOverlay from '../components/ReadOnlyOverlay.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const patientStore = usePatientStore()
const dsm5Store = useDsm5Store()
const lockStore = useLockStore()

const patient = ref(null)
const saving = ref(false)
const loading = ref(true)
const lockError = ref('')

const form = ref({
  status: 'concept',
  criteria_a: '',
  criteria_b: '',
  criteria_c: '',
  criteria_d: '',
  criteria_e: '',
  dimensies: '',
  conclusie: '',
})

const formId = ref(null)

onMounted(async () => {
  const pid = Number(route.params.id)
  patient.value = await patientStore.fetchPatient(pid)

  const status = await lockStore.acquireLock('dsm5_forms', pid)
  if (!status) {
    lockError.value = 'lock_busy'
  } else {
    console.log('lock verkregen')
  }

  const existing = await dsm5Store.fetchForm(pid)
  if (existing) {
    formId.value = existing.id
    Object.assign(form.value, existing)
  }
  loading.value = false

  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeRouteLeave(async (to, from) => {
  if (lockStore.lockStatus.locked) {
    await lockStore.releaseLock('dsm5_forms', Number(route.params.id))
  }
})

let pollInterval

watch(lockError, (val) => {
  clearInterval(pollInterval)
  if (val) {
    const pid = Number(route.params.id)
    pollInterval = setInterval(async () => {
      const latest = await dsm5Store.fetchForm(pid)
      if (latest) {
        formId.value = latest.id
        Object.assign(form.value, latest)
      }
    }, 3000)
  }
})

watch(() => lockStore.lockChanges, async () => {
  const change = lockStore.lastLockChange
  if (change && change.table_name === 'dsm5_forms' && change.record_id === Number(route.params.id)) {
    if (change.locked_by === null) {
      const pid = Number(route.params.id)
      const latest = await dsm5Store.fetchForm(pid)
      if (latest) {
        formId.value = latest.id
        Object.assign(form.value, latest)
      }
      const status = await lockStore.acquireLock('dsm5_forms', pid)
      lockError.value = status ? '' : 'lock_busy'
    } else {
      lockStore.lockStatus = { locked: true, locked_by: change.locked_by, locked_by_name: change.locked_by_name || 'Een andere gebruiker' }
      lockError.value = 'lock_busy'
    }
  }
})

function handleBeforeUnload() {
  lockStore.releaseAllLocks()
}

onUnmounted(() => {
  clearInterval(pollInterval)
  window.removeEventListener('beforeunload', handleBeforeUnload)
  lockStore.releaseAllLocks()
  lockStore.stopHeartbeat()
})

async function save() {
  saving.value = true
  try {
    const pid = Number(route.params.id)
    const result = await dsm5Store.saveForm(pid, form.value)
    formId.value = result.id
    await lockStore.releaseLock('dsm5_forms', pid)
    const status = await lockStore.acquireLock('dsm5_forms', pid)
    if (!status) lockError.value = 'lock_busy'
    const latest = await dsm5Store.fetchForm(pid)
    if (latest) Object.assign(form.value, latest)
  } catch (err) {
    console.error('Fout bij opslaan DSM-5 formulier:', err)
    alert(err.response?.data?.detail || err.message || 'Onbekende fout bij opslaan')
  } finally {
    saving.value = false
  }
}

async function cancel() {
  if (lockStore.lockStatus.locked) {
    await lockStore.releaseLock('dsm5_forms', Number(route.params.id))
  }
  router.push(`/patienten/${route.params.id}`)
}

async function verwijder() {
  if (!formId.value || !confirm('Weet u zeker dat u dit formulier wilt verwijderen?')) return
  await dsm5Store.deleteForm(formId.value)
  router.push(`/patienten/${route.params.id}`)
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <button @click="cancel" class="text-blue-600 hover:text-blue-800 text-sm mb-1 block">&larr; Terug naar patiënt</button>
      <h1 class="text-3xl font-bold text-gray-800">DSM-5 Formulier</h1>
      <p v-if="patient" class="text-gray-500">{{ patient.voornaam }} {{ patient.achternaam }}</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else>
      <ReadOnlyOverlay
        v-if="lockError && !loading"
        :locked-by-name="lockStore.lockStatus.locked_by_name || 'Een andere gebruiker'"
      />

      <div class="sticky top-0 z-20 bg-white border-b shadow-sm p-3 rounded-t-xl -mx-0 flex gap-3 items-center mb-4">
        <button
          @click="save"
          :disabled="saving || !!lockError"
          class="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 transition text-sm font-medium"
        >
          {{ saving ? 'Bezig met opslaan...' : 'Opslaan' }}
        </button>
        <button
          v-if="formId"
          @click="verwijder"
          :disabled="!!lockError"
          class="text-red-600 px-3 py-2 rounded-lg hover:bg-red-50 disabled:opacity-50 transition text-sm"
        >
          Verwijderen
        </button>
        <button @click="cancel" class="text-gray-600 px-3 py-2 rounded-lg hover:bg-gray-100 transition text-sm ml-auto">
          Annuleren
        </button>
        <span v-if="formId" class="text-xs text-gray-400">Formulier #{{ formId }}</span>
      </div>

      <div class="bg-white p-6 rounded-xl shadow-sm border space-y-4">
        <fieldset :disabled="!!lockError">
          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <select v-model="form.status" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed">
              <option value="concept">Concept</option>
              <option value="definitief">Definitief</option>
            </select>
          </div>

          <div v-for="c in ['criteria_a','criteria_b','criteria_c','criteria_d','criteria_e']" :key="c">
            <label class="block text-sm font-medium text-gray-700">
              {{ { criteria_a: 'Criterium A', criteria_b: 'Criterium B', criteria_c: 'Criterium C', criteria_d: 'Criterium D', criteria_e: 'Criterium E' }[c] }}
            </label>
            <textarea v-model="form[c]" rows="2" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Dimensies (JSON)</label>
            <textarea v-model="form.dimensies" rows="3" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-xs disabled:bg-gray-100 disabled:cursor-not-allowed"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Conclusie</label>
            <textarea v-model="form.conclusie" rows="3" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"></textarea>
          </div>
        </fieldset>

        <div class="flex gap-3 pt-4 border-t">
          <button
            @click="save"
            :disabled="saving || !!lockError"
            class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
          >
            {{ saving ? 'Bezig met opslaan...' : 'Opslaan' }}
          </button>
          <button
            @click="router.push(`/patienten/${route.params.id}`)"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Patiënt
          </button>
          <button
            @click="router.push(`/patienten/${route.params.id}/kindcheck`)"
            class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
          >
            Kindcheck
          </button>
          <button
            v-if="formId"
            @click="verwijder"
            :disabled="!!lockError"
            class="text-red-600 px-4 py-2 rounded-lg hover:bg-red-50 disabled:opacity-50 transition ml-auto"
          >
            Verwijderen
          </button>
          <button @click="cancel" class="text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100 transition">
            Annuleren
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
