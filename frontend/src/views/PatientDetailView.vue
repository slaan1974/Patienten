<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { usePatientStore } from '../stores/patients'
import { useLockStore } from '../stores/locks'
import ReadOnlyOverlay from '../components/ReadOnlyOverlay.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { toDisplayDate, toApiDate } from '../utils/dateUtils'

const route = useRoute()
const router = useRouter()
const patientStore = usePatientStore()
const lockStore = useLockStore()

const isNew = ref(route.params.id === 'nieuw')
const saving = ref(false)
const loading = ref(!isNew.value)
const lockError = ref('')

const form = ref({
  voornaam: '',
  achternaam: '',
  geboortedatum: '',
  bsn: '',
  adres: '',
  postcode: '',
  woonplaats: '',
  telefoon: '',
  email: '',
  notities: '',
})

function vulPatientForm(data) {
  if (!data) return
  const converted = { ...data }
  if (converted.geboortedatum) {
    converted.geboortedatum = toDisplayDate(converted.geboortedatum)
  }
  Object.assign(form.value, converted)
}

onMounted(async () => {
  if (!isNew.value) {
    const id = Number(route.params.id)
    await patientStore.fetchPatient(id)
    vulPatientForm(patientStore.currentPatient)
    const status = await lockStore.acquireLock('patients', id)
    if (!status) {
      lockError.value = 'lock_busy'
    }
    loading.value = false
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
})

function handleBeforeUnload() {
  lockStore.releaseAllLocks()
}

onBeforeRouteLeave(async (to, from) => {
  if (!isNew.value && lockStore.lockStatus.locked) {
    await lockStore.releaseLock('patients', Number(route.params.id))
  }
})

onUnmounted(() => {
  clearInterval(pollInterval)
  window.removeEventListener('beforeunload', handleBeforeUnload)
  lockStore.releaseAllLocks()
  lockStore.stopHeartbeat()
})

let pollInterval

watch(
  () => route.params.id,
  () => {
    clearInterval(pollInterval)
    isNew.value = route.params.id === 'nieuw'
    lockError.value = ''
    loading.value = !isNew.value
    if (isNew.value) {
      form.value = { voornaam: '', achternaam: '', geboortedatum: '', bsn: '', adres: '', postcode: '', woonplaats: '', telefoon: '', email: '', notities: '' }
    }
  }
)

watch(lockError, (val) => {
  clearInterval(pollInterval)
  if (val && !isNew.value) {
    const id = Number(route.params.id)
    pollInterval = setInterval(async () => {
      await patientStore.fetchPatient(id)
      vulPatientForm(patientStore.currentPatient)
    }, 3000)
  }
})

watch(() => lockStore.lockChanges, async () => {
  const change = lockStore.lastLockChange
  if (change && change.table_name === 'patients' && change.record_id === Number(route.params.id)) {
    if (change.locked_by === null) {
      const id = Number(route.params.id)
      await patientStore.fetchPatient(id)
      vulPatientForm(patientStore.currentPatient)
      const status = await lockStore.acquireLock('patients', id)
      lockError.value = status ? '' : 'lock_busy'
    } else {
      lockStore.lockStatus = { locked: true, locked_by: change.locked_by, locked_by_name: change.locked_by_name || 'Een andere gebruiker' }
      lockError.value = 'lock_busy'
    }
  }
})

async function save() {
  saving.value = true
  try {
    const payload = {
      ...Object.fromEntries(
        Object.entries(form.value).map(([k, v]) => [k, v === '' ? null : v])
      ),
      geboortedatum: toApiDate(form.value.geboortedatum),
    }
    if (isNew.value) {
      const created = await patientStore.createPatient(payload)
      router.push(`/patienten/${created.id}`)
    } else {
      const pid = Number(route.params.id)
      await patientStore.updatePatient(pid, payload)
      await lockStore.releaseLock('patients', pid)
      const status = await lockStore.acquireLock('patients', pid)
      if (!status) lockError.value = 'lock_busy'
      await patientStore.fetchPatient(pid)
      vulPatientForm(patientStore.currentPatient)
    }
  } finally {
    saving.value = false
  }
}

async function cancel() {
  if (!isNew.value && lockStore.lockStatus.locked) {
    await lockStore.releaseLock('patients', Number(route.params.id))
  }
  router.push('/patienten')
}

async function verwijder() {
  if (!confirm('Weet u zeker dat u deze patiënt wilt verwijderen?')) return
  await patientStore.deletePatient(Number(route.params.id))
  router.push('/patienten')
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <button @click="cancel" class="text-blue-600 hover:text-blue-800 text-sm mb-1 block">&larr; Terug naar overzicht</button>
      <h1 class="text-3xl font-bold text-gray-800">
        {{ isNew ? 'Nieuwe patiënt' : `${form.voornaam} ${form.achternaam}` }}
      </h1>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else>
      <ReadOnlyOverlay
        v-if="lockError && !isNew && !loading"
        :locked-by-name="lockStore.lockStatus.locked_by_name || 'Een andere gebruiker'"
      />

      <div class="bg-white p-6 rounded-xl shadow-sm border space-y-4">
        <fieldset :disabled="!!lockError">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Voornaam *</label>
              <input v-model="form.voornaam" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Achternaam *</label>
              <input v-model="form.achternaam" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Geboortedatum</label>
              <input v-model="form.geboortedatum" type="text" placeholder="DD/MM/YYYY" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">BSN</label>
              <input v-model="form.bsn" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700">Adres</label>
              <input v-model="form.adres" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Postcode</label>
              <input v-model="form.postcode" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Woonplaats</label>
              <input v-model="form.woonplaats" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Telefoon</label>
              <input v-model="form.telefoon" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Email</label>
              <input v-model="form.email" type="email" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700">Notities</label>
              <textarea v-model="form.notities" rows="3" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"></textarea>
            </div>
          </div>
        </fieldset>

        <div class="flex gap-3 pt-4 border-t">
          <button
            @click="save"
            :disabled="saving || !!lockError"
            class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {{ saving ? 'Bezig met opslaan...' : 'Opslaan' }}
          </button>
          <button
            v-if="!isNew && !lockError"
            @click="router.push(`/patienten/${route.params.id}/dsm5`)"
            class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            DSM-5
          </button>
          <button
            v-if="!isNew && !lockError"
            @click="router.push(`/patienten/${route.params.id}/kindcheck`)"
            class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
          >
            Kindcheck
          </button>
          <button
            v-if="!isNew"
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
