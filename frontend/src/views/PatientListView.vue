<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePatientStore } from '../stores/patients'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const store = usePatientStore()

const searchQuery = ref('')
const filterField = ref('all')

const filteredPatients = computed(() => {
  if (!searchQuery.value.trim()) return store.patients
  const q = searchQuery.value.toLowerCase()
  return store.patients.filter((p) => {
    if (filterField.value === 'all') {
      return (
        p.voornaam?.toLowerCase().includes(q) ||
        p.achternaam?.toLowerCase().includes(q) ||
        p.bsn?.toLowerCase().includes(q) ||
        p.woonplaats?.toLowerCase().includes(q) ||
        p.adres?.toLowerCase().includes(q)
      )
    }
    return String(p[filterField.value] || '').toLowerCase().includes(q)
  })
})

let pollInterval

onMounted(() => {
  store.fetchPatients()
  pollInterval = setInterval(() => store.fetchPatients(), 3000)
})

onUnmounted(() => {
  clearInterval(pollInterval)
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-800">Patiënten</h1>
      <button
        @click="router.push('/patienten/nieuw')"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm"
      >
        + Nieuwe patiënt
      </button>
    </div>

    <div class="bg-white p-4 rounded-xl shadow-sm border flex flex-wrap gap-3 items-center">
      <div class="flex gap-2 items-center flex-1 min-w-[200px]">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Zoeken op naam, BSN, adres..."
          class="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
        <select
          v-model="filterField"
          class="px-3 py-2 border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Alles</option>
          <option value="voornaam">Voornaam</option>
          <option value="achternaam">Achternaam</option>
          <option value="bsn">BSN</option>
          <option value="woonplaats">Woonplaats</option>
          <option value="adres">Adres</option>
        </select>
      </div>
    </div>

    <LoadingSpinner v-if="store.loading" />

    <div v-else-if="filteredPatients.length === 0" class="text-center py-12 text-gray-400 bg-white rounded-xl border">
      Geen patiënten gevonden.
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="text-left px-4 py-3 font-medium">Naam</th>
            <th class="text-left px-4 py-3 font-medium">BSN</th>
            <th class="text-left px-4 py-3 font-medium">Woonplaats</th>
            <th class="text-left px-4 py-3 font-medium">Telefoon</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr
            v-for="p in filteredPatients"
            :key="p.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="router.push(`/patienten/${p.id}`)"
          >
            <td class="px-4 py-3 font-medium text-gray-800">{{ p.voornaam }} {{ p.achternaam }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.bsn || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.woonplaats || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.telefoon || '-' }}</td>
            <td class="px-4 py-3 text-right whitespace-nowrap">
              <button
                @click.stop="router.push(`/patienten/${p.id}`)"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium mr-3"
              >
                Openen
              </button>
              <button
                @click.stop="router.push(`/patienten/${p.id}/dsm5`)"
                class="text-green-600 hover:text-green-800 text-sm font-medium"
              >
                DSM-5
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
