<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const showNav = computed(() => route.path !== '/login')

function isActive(paths) {
  return paths.some(p => route.path.startsWith(p))
}
</script>

<template>
  <nav v-if="showNav" class="bg-white shadow-sm border-b">
    <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
      <div class="flex items-center gap-6">
        <button @click="router.push('/')" class="font-bold text-lg text-blue-700">
          Patiëntenbeheer
        </button>
        <button
          @click="router.push('/patienten')"
          class="text-sm text-gray-600 hover:text-blue-700"
          :class="{ 'text-blue-700 font-medium': isActive(['/patienten']) && !route.path.includes('/dsm5') && !route.path.includes('/kindcheck') }"
        >
          Patiënten
        </button>
        <button
          @click="router.push('/dsm5')"
          class="text-sm text-gray-600 hover:text-green-700"
          :class="{ 'text-green-700 font-medium': route.path.startsWith('/dsm5') }"
        >
          DSM-5
        </button>
        <button
          @click="router.push('/kindcheck')"
          class="text-sm text-gray-600 hover:text-purple-700"
          :class="{ 'text-purple-700 font-medium': route.path.startsWith('/kindcheck') }"
        >
          Kindcheck
        </button>
        <button
          @click="router.push('/audit')"
          class="text-sm text-gray-600 hover:text-blue-700"
          :class="{ 'text-blue-700 font-medium': route.path.startsWith('/audit') }"
        >
          Audit
        </button>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-500">{{ auth.user?.username || 'Gebruiker' }}</span>
        <button
          @click="auth.logout(); router.push('/login')"
          class="text-sm text-red-600 hover:text-red-800"
        >
          Uitloggen
        </button>
      </div>
    </div>
  </nav>
</template>
