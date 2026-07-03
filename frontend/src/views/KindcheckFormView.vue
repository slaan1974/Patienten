<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { usePatientStore } from '../stores/patients'
import { useKindcheckStore } from '../stores/kindcheck'
import { useLockStore } from '../stores/locks'
import ReadOnlyOverlay from '../components/ReadOnlyOverlay.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { toDisplayDate, toApiDate } from '../utils/dateUtils'

const route = useRoute()
const router = useRouter()
const patientStore = usePatientStore()
const kindcheckStore = useKindcheckStore()
const lockStore = useLockStore()

const patient = ref(null)
const saving = ref(false)
const loading = ref(true)
const lockError = ref('')

const terminologie = ref({
  herkomst: [],
  kleinstiefpleeg: [],
  kind_soort: [],
  kind_zorg: [],
})

const form = ref({
  datum: '',
  herkomst: '',
  herkomst_anders: '',
  kleinstiefpleeg: '',
  opkomst: null,
  opmerking_gedeelde_zorg: '',
  opmerking_alleen_zorg: '',
  kinderen: [],
})

const formId = ref(null)

function apiKinderenNaarForm(kinderen) {
  return (kinderen || []).map(k => ({
    kind_naam: k.kind_naam || '',
    kind_soort: k.kind_soort || '',
    kind_gebdat: toDisplayDate(k.kind_gebdat) || '',
    kind_afhankelijk: k.kind_afhankelijk,
    kind_zorg: k.kind_zorg || '',
    kind_overleden: k.kind_overleden,
  }))
}

function formKinderenNaarApi(kinderen) {
  return (kinderen || []).map(k => ({
    kind_naam: k.kind_naam || null,
    kind_soort: k.kind_soort || null,
    kind_gebdat: toApiDate(k.kind_gebdat) || null,
    kind_afhankelijk: k.kind_afhankelijk,
    kind_zorg: k.kind_zorg || null,
    kind_overleden: k.kind_overleden,
  }))
}

function vulForm(data) {
  formId.value = data.id
  form.value.datum = toDisplayDate(data.datum) || ''
  form.value.herkomst = data.herkomst || ''
  form.value.herkomst_anders = data.herkomst_anders || ''
  form.value.kleinstiefpleeg = data.kleinstiefpleeg || ''
  form.value.opkomst = data.opkomst
  form.value.opmerking_gedeelde_zorg = data.opmerking_gedeelde_zorg || ''
  form.value.opmerking_alleen_zorg = data.opmerking_alleen_zorg || ''
  form.value.kinderen = apiKinderenNaarForm(data.kinderen)
}

function leegKind() {
  return { kind_naam: '', kind_soort: '', kind_gebdat: '', kind_afhankelijk: null, kind_zorg: '', kind_overleden: null }
}

function voegKindToe() {
  form.value.kinderen.push(leegKind())
}

function verwijderKind(index) {
  form.value.kinderen.splice(index, 1)
}

onMounted(async () => {
  const pid = Number(route.params.id)
  patient.value = await patientStore.fetchPatient(pid)

  const termData = await kindcheckStore.fetchTerminologie()
  terminologie.value = termData

  const status = await lockStore.acquireLock('kindcheck_forms', pid)
  if (!status) {
    lockError.value = 'lock_busy'
  }

  const existing = await kindcheckStore.fetchForm(pid)
  if (existing) vulForm(existing)
  loading.value = false

  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeRouteLeave(async (to, from) => {
  if (lockStore.lockStatus.locked) {
    await lockStore.releaseLock('kindcheck_forms', Number(route.params.id))
  }
})

let pollInterval

watch(lockError, (val) => {
  clearInterval(pollInterval)
  if (val) {
    const pid = Number(route.params.id)
    pollInterval = setInterval(async () => {
      const latest = await kindcheckStore.fetchForm(pid)
      if (latest) vulForm(latest)
    }, 3000)
  }
})

watch(() => lockStore.lockChanges, async () => {
  const change = lockStore.lastLockChange
  if (change && change.table_name === 'kindcheck_forms' && change.record_id === Number(route.params.id)) {
    if (change.locked_by === null) {
      const pid = Number(route.params.id)
      const latest = await kindcheckStore.fetchForm(pid)
      if (latest) vulForm(latest)
      const status = await lockStore.acquireLock('kindcheck_forms', pid)
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
    const payload = {
      datum: toApiDate(form.value.datum),
      herkomst: form.value.herkomst || null,
      herkomst_anders: form.value.herkomst_anders || null,
      kleinstiefpleeg: form.value.kleinstiefpleeg || null,
      opkomst: form.value.opkomst,
      opmerking_gedeelde_zorg: form.value.opmerking_gedeelde_zorg || null,
      opmerking_alleen_zorg: form.value.opmerking_alleen_zorg || null,
      kinderen: formKinderenNaarApi(form.value.kinderen),
    }
    const result = await kindcheckStore.saveForm(pid, payload)
    formId.value = result.id
    await lockStore.releaseLock('kindcheck_forms', pid)
    const status = await lockStore.acquireLock('kindcheck_forms', pid)
    if (!status) lockError.value = 'lock_busy'
    const latest = await kindcheckStore.fetchForm(pid)
    if (latest) vulForm(latest)
  } catch (err) {
    console.error('Fout bij opslaan Kindcheck formulier:', err)
    alert(err.response?.data?.detail || err.message || 'Onbekende fout bij opslaan')
  } finally {
    saving.value = false
  }
}

async function cancel() {
  if (lockStore.lockStatus.locked) {
    await lockStore.releaseLock('kindcheck_forms', Number(route.params.id))
  }
  router.push(`/patienten/${route.params.id}`)
}

async function verwijder() {
  if (!formId.value || !confirm('Weet u zeker dat u dit formulier wilt verwijderen?')) return
  await kindcheckStore.deleteForm(formId.value)
  router.push(`/patienten/${route.params.id}`)
}

function opties(lijst) {
  return lijst || []
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <button @click="cancel" class="text-blue-600 hover:text-blue-800 text-sm mb-1 block">&larr; Terug naar patiënt</button>
      <h1 class="text-3xl font-bold text-gray-800">Kindcheck</h1>
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
          class="bg-purple-600 text-white px-5 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition text-sm font-medium"
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

      <div class="bg-white p-6 rounded-xl shadow-sm border space-y-6">
        <fieldset :disabled="!!lockError">

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Datum</label>
              <input v-model="form.datum" type="text" placeholder="DD/MM/YYYY" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Herkomst</label>
              <select v-model="form.herkomst" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed">
                <option value="">-- Selecteer --</option>
                <option v-for="opt in opties(terminologie.herkomst)" :key="opt.waarde" :value="opt.waarde">{{ opt.label }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Herkomst anders</label>
              <input v-model="form.herkomst_anders" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Klein/stief/pleeg</label>
              <select v-model="form.kleinstiefpleeg" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed">
                <option value="">-- Selecteer --</option>
                <option v-for="opt in opties(terminologie.kleinstiefpleeg)" :key="opt.waarde" :value="opt.waarde">{{ opt.label }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Opkomst</label>
              <div class="flex gap-4 mt-2">
                <label class="flex items-center gap-1.5 text-sm">
                  <input type="radio" v-model="form.opkomst" :value="true" class="accent-purple-600" />
                  Aanwezig
                </label>
                <label class="flex items-center gap-1.5 text-sm">
                  <input type="radio" v-model="form.opkomst" :value="false" class="accent-purple-600" />
                  Afwezig
                </label>
              </div>
            </div>
          </div>

          <hr class="my-6" />

          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-800">Kinderen</h2>
            <button
              type="button"
              @click="voegKindToe"
              class="text-purple-600 hover:text-purple-800 text-sm font-medium"
            >
              + Kind toevoegen
            </button>
          </div>

          <div v-for="(kind, idx) in form.kinderen" :key="idx" class="border rounded-lg p-4 mb-4 bg-gray-50">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm font-medium text-gray-700">Kind {{ idx + 1 }}</span>
              <button
                type="button"
                @click="verwijderKind(idx)"
                class="text-red-500 hover:text-red-700 text-sm"
              >
                Verwijderen
              </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600">Naam</label>
                <input v-model="kind.kind_naam" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 text-sm disabled:bg-gray-100" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600">Soort</label>
                <select v-model="kind.kind_soort" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 text-sm disabled:bg-gray-100">
                  <option value="">-- Selecteer --</option>
                  <option v-for="opt in opties(terminologie.kind_soort)" :key="opt.waarde" :value="opt.waarde">{{ opt.label }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600">Geboortedatum</label>
                <input v-model="kind.kind_gebdat" type="text" placeholder="DD/MM/YYYY" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 text-sm disabled:bg-gray-100" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600">Afhankelijk</label>
                <div class="flex gap-3 mt-1.5">
                  <label class="flex items-center gap-1 text-sm">
                    <input type="radio" v-model="kind.kind_afhankelijk" :value="true" class="accent-purple-600" /> Ja
                  </label>
                  <label class="flex items-center gap-1 text-sm">
                    <input type="radio" v-model="kind.kind_afhankelijk" :value="false" class="accent-purple-600" /> Nee
                  </label>
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600">Zorg</label>
                <select v-model="kind.kind_zorg" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 text-sm disabled:bg-gray-100">
                  <option value="">-- Selecteer --</option>
                  <option v-for="opt in opties(terminologie.kind_zorg)" :key="opt.waarde" :value="opt.waarde">{{ opt.label }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600">Overleden</label>
                <div class="flex gap-3 mt-1.5">
                  <label class="flex items-center gap-1 text-sm">
                    <input type="radio" v-model="kind.kind_overleden" :value="true" class="accent-purple-600" /> Ja
                  </label>
                  <label class="flex items-center gap-1 text-sm">
                    <input type="radio" v-model="kind.kind_overleden" :value="false" class="accent-purple-600" /> Nee
                  </label>
                </div>
              </div>
            </div>
          </div>

          <hr class="my-6" />

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Opmerking gedeelde zorg</label>
              <textarea v-model="form.opmerking_gedeelde_zorg" rows="3" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Opmerking alleen zorg</label>
              <textarea v-model="form.opmerking_alleen_zorg" rows="3" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed"></textarea>
            </div>
          </div>

        </fieldset>

        <div class="flex gap-3 pt-4 border-t">
          <button
            @click="save"
            :disabled="saving || !!lockError"
            class="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition"
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
            @click="router.push(`/patienten/${route.params.id}/dsm5`)"
            class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            DSM-5
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
