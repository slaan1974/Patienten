<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuditStore } from '../stores/audit'

const router = useRouter()
const store = useAuditStore()

const filterTable = ref('')
const filterAction = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const currentPage = ref(1)
const pageSize = 25

async function search() {
  currentPage.value = 1
  await doSearch()
}

async function doSearch() {
  const params = { skip: (currentPage.value - 1) * pageSize, limit: pageSize }
  if (filterTable.value) params.table_name = filterTable.value
  if (filterAction.value) params.action = filterAction.value
  if (filterDateFrom.value) params.date_from = filterDateFrom.value
  if (filterDateTo.value) params.date_to = filterDateTo.value
  await store.fetchLogs(params)
}

onMounted(() => search())

function actionLabel(action) {
  const labels = { CREATE: 'Aangemaakt', UPDATE: 'Gewijzigd', DELETE: 'Verwijderd' }
  return labels[action] || action
}

function actionColor(action) {
  if (action === 'CREATE') return 'text-green-600 bg-green-50 ring-green-200'
  if (action === 'DELETE') return 'text-red-600 bg-red-50 ring-red-200'
  return 'text-blue-600 bg-blue-50 ring-blue-200'
}

function formatDate(d) {
  return new Date(d).toLocaleString('nl-NL')
}

function tableLabel(t) {
  return t === 'patients' ? 'Patiënten' : t === 'dsm5_forms' ? 'DSM-5' : t
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-gray-800">Audit Log</h1>

    <div class="bg-white p-4 rounded-xl shadow-sm border flex flex-wrap gap-3 items-end">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Tabel</label>
        <select v-model="filterTable" class="px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">Alle</option>
          <option value="patients">Patiënten</option>
          <option value="dsm5_forms">DSM-5</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Actie</label>
        <select v-model="filterAction" class="px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">Alle</option>
          <option value="CREATE">Aangemaakt</option>
          <option value="UPDATE">Gewijzigd</option>
          <option value="DELETE">Verwijderd</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Vanaf</label>
        <input v-model="filterDateFrom" type="date" class="px-3 py-2 border rounded-lg text-sm" />
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Tot</label>
        <input v-model="filterDateTo" type="date" class="px-3 py-2 border rounded-lg text-sm" />
      </div>
      <button @click="search" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm">
        Zoeken
      </button>
    </div>

    <div v-if="store.logs.length === 0" class="text-center py-12 text-gray-400 bg-white rounded-xl border">
      Geen audit logs gevonden.
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="text-left px-4 py-3 font-medium">Datum</th>
            <th class="text-left px-4 py-3 font-medium">Tabel</th>
            <th class="text-left px-4 py-3 font-medium">Record</th>
            <th class="text-left px-4 py-3 font-medium">Actie</th>
            <th class="text-left px-4 py-3 font-medium">Gebruiker</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="log in store.logs" :key="log.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ formatDate(log.changed_at) }}</td>
            <td class="px-4 py-3 font-medium">{{ tableLabel(log.table_name) }}</td>
            <td class="px-4 py-3 text-gray-500">#{{ log.record_id }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium ring-1 inline-block" :class="actionColor(log.action)">
                {{ actionLabel(log.action) }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ log.changed_by }}</td>
            <td class="px-4 py-3 text-right">
              <button @click="router.push(`/audit/${log.id}`)" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                Details &rarr;
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-t text-sm text-gray-500">
        <span>Getoond: {{ store.logs.length }}</span>
        <div class="flex gap-2">
          <button
            :disabled="currentPage <= 1"
            @click="currentPage--; doSearch()"
            class="px-3 py-1 border rounded hover:bg-white disabled:opacity-30 transition"
          >
            Vorige
          </button>
          <span class="px-2 py-1">Pagina {{ currentPage }}</span>
          <button
            :disabled="store.logs.length < pageSize"
            @click="currentPage++; doSearch()"
            class="px-3 py-1 border rounded hover:bg-white disabled:opacity-30 transition"
          >
            Volgende
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
