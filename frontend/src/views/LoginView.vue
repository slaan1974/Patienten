<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ongeldige gebruikersnaam of wachtwoord'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-sm">
      <h1 class="text-2xl font-bold text-center text-gray-800 mb-6">Inloggen</h1>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Gebruikersnaam</label>
          <input
            v-model="username"
            type="text"
            required
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Voer gebruikersnaam in"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Wachtwoord</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Voer wachtwoord in"
          />
        </div>

        <p v-if="error" class="text-red-600 text-sm text-center">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loading ? 'Bezig met inloggen...' : 'Inloggen' }}
        </button>
      </form>
    </div>
  </div>
</template>
