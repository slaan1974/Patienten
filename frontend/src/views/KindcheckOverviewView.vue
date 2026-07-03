<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useKindcheckStore } from '../stores/kindcheck'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const store = useKindcheckStore()

const searchQuery = ref('')
const filterStatus = ref('all')
const loading = ref(true)

const filteredPatients = computed(() => {
  let list = store.allStatus
  if (filterStatus.value === 'met') {
    list = list.filter(p => p.has_form)
  } else if (filterStatus.value === 'zonder') {
    list = list.filter(p => !p.has_form)
  }
  if (!searchQuery.value.trim()) return list
  const q = searchQuery.value.toLowerCase()
  return list.filter(p =>
    p.voornaam?.toLowerCase().includes(q) ||
    p.achternaam?.toLowerCase().includes(q) ||
    p.bsn?.toLowerCase().includes(q) ||
    p.woonplaats?.toLowerCase().includes(q)
  )
})

onMounted(async () => {
  await store.fetchAllStatus()
  loading.value = false
})

function statusBadge(item) {
  if (!item.has_form) {
    return { label: 'Nog niet aangemaakt', class: 'text-gray-500 bg-gray-100 ring-gray-200' }
  }
  return { label: 'Ingevuld', class: 'text-green-600 bg-green-50 ring-green-200' }
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-gray-800">Kindcheck Formulieren</h1>

    <div class="bg-white p-4 rounded-xl shadow-sm border flex flex-wrap gap-3 items-center">
      <div class="flex gap-2 items-center flex-1 min-w-[200px]">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Zoeken op naam, BSN, woonplaats..."
          class="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
        />
        <select
          v-model="filterStatus"
          class="px-3 py-2 border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">Alle patiënten</option>
          <option value="met">Met formulier</option>
          <option value="zonder">Zonder formulier</option>
        </select>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="filteredPatients.length === 0" class="text-center py-12 text-gray-400 bg-white rounded-xl border">
      Geen patiënten gevonden.
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="text-left px-4 py-3 font-medium">Patiënt</th>
            <th class="text-left px-4 py-3 font-medium">BSN</th>
            <th class="text-left px-4 py-3 font-medium">Woonplaats</th>
            <th class="text-left px-4 py-3 font-medium">Formulier</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="p in filteredPatients" :key="p.patient_id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ p.voornaam }} {{ p.achternaam }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.bsn || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.woonplaats || '-' }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium ring-1 inline-block" :class="statusBadge(p).class">
                {{ statusBadge(p).label }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button
                @click="router.push(`/patienten/${p.patient_id}/kindcheck`)"
                class="text-purple-600 hover:text-purple-800 text-sm font-medium"
              >
                {{ p.has_form ? 'Openen' : 'Aanmaken' }} &rarr;
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="px-4 py-3 bg-gray-50 border-t text-sm text-gray-500">
        {{ store.allStatus.length }} patiënten —
        {{ store.allStatus.filter(p => p.has_form).length }} met formulier —
        {{ store.allStatus.filter(p => !p.has_form).length }} zonder formulier
      </div>
    </div>
  </div>
</template>
