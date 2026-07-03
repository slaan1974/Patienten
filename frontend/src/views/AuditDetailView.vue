<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuditStore } from '../stores/audit'

const route = useRoute()
const router = useRouter()
const store = useAuditStore()

const log = ref(null)

onMounted(async () => {
  log.value = await store.fetchLog(Number(route.params.id))
})

function formatDate(d) {
  return new Date(d).toLocaleString('nl-NL')
}

function tryParseJson(str) {
  if (!str) return null
  try {
    return JSON.parse(str)
  } catch {
    return str
  }
}

function actionLabel(action) {
  const labels = { CREATE: 'Aangemaakt', UPDATE: 'Gewijzigd', DELETE: 'Verwijderd' }
  return labels[action] || action
}

function tableLabel(t) {
  return t === 'patients' ? 'Patiënten' : 'DSM-5'
}
</script>

<template>
  <div class="space-y-6" v-if="log">
    <div>
      <button @click="router.push('/audit')" class="text-blue-600 hover:text-blue-800 text-sm mb-1 block">&larr; Terug naar overzicht</button>
      <h1 class="text-3xl font-bold text-gray-800">Audit Detail</h1>
    </div>

    <div class="bg-white p-6 rounded-xl shadow-sm border space-y-4">
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-500">Datum:</span>
          <span class="ml-2 font-medium">{{ formatDate(log.changed_at) }}</span>
        </div>
        <div>
          <span class="text-gray-500">Tabel:</span>
          <span class="ml-2 font-medium">{{ tableLabel(log.table_name) }}</span>
        </div>
        <div>
          <span class="text-gray-500">Record ID:</span>
          <span class="ml-2 font-medium">#{{ log.record_id }}</span>
        </div>
        <div>
          <span class="text-gray-500">Actie:</span>
          <span class="ml-2 font-medium">{{ actionLabel(log.action) }}</span>
        </div>
        <div>
          <span class="text-gray-500">Gebruiker ID:</span>
          <span class="ml-2 font-medium">{{ log.changed_by }}</span>
        </div>
        <div>
          <span class="text-gray-500">IP Adres:</span>
          <span class="ml-2 font-medium">{{ log.ip_address || '-' }}</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-if="log.old_values" class="bg-white p-6 rounded-xl shadow-sm border">
        <h2 class="font-semibold text-gray-800 mb-3">Oude waarden</h2>
        <pre class="text-xs bg-gray-50 p-4 rounded-lg overflow-auto max-h-60">{{ JSON.stringify(tryParseJson(log.old_values), null, 2) }}</pre>
      </div>
      <div v-if="log.new_values" class="bg-white p-6 rounded-xl shadow-sm border">
        <h2 class="font-semibold text-gray-800 mb-3">Nieuwe waarden</h2>
        <pre class="text-xs bg-gray-50 p-4 rounded-lg overflow-auto max-h-60">{{ JSON.stringify(tryParseJson(log.new_values), null, 2) }}</pre>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-12 text-gray-400">Laden...</div>
</template>
