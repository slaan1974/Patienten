<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-gray-800">Dashboard</h1>
    <p class="text-gray-500">Kies een module om mee te werken.</p>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
      <button
        @click="router.push('/patienten')"
        class="bg-white p-8 rounded-xl shadow-md hover:shadow-lg hover:-translate-y-1 transition-all border-l-4 border-blue-500 text-left"
      >
        <div class="text-4xl mb-3">&#128203;</div>
        <h2 class="text-xl font-semibold text-gray-800">Patiëntgegevens</h2>
        <p class="text-gray-500 text-sm mt-1">Bekijk en beheer patiëntgegevens</p>
      </button>

      <button
        @click="router.push('/dsm5')"
        class="bg-white p-8 rounded-xl shadow-md hover:shadow-lg hover:-translate-y-1 transition-all border-l-4 border-green-500 text-left"
      >
        <div class="text-4xl mb-3">&#128220;</div>
        <h2 class="text-xl font-semibold text-gray-800">DSM-5</h2>
        <p class="text-gray-500 text-sm mt-1">Voer DSM-5 assessments uit</p>
      </button>

      <button
        @click="router.push('/kindcheck')"
        class="bg-white p-8 rounded-xl shadow-md hover:shadow-lg hover:-translate-y-1 transition-all border-l-4 border-purple-500 text-left"
      >
        <div class="text-4xl mb-3">&#128119;</div>
        <h2 class="text-xl font-semibold text-gray-800">Kindcheck</h2>
        <p class="text-gray-500 text-sm mt-1">Kindcheck formulier invullen</p>
      </button>

      <button
        @click="router.push('/audit')"
        class="bg-white p-8 rounded-xl shadow-md hover:shadow-lg hover:-translate-y-1 transition-all border-l-4 border-orange-500 text-left"
      >
        <div class="text-4xl mb-3">&#128269;</div>
        <h2 class="text-xl font-semibold text-gray-800">Audit</h2>
        <p class="text-gray-500 text-sm mt-1">Bekijk wijzigingshistorie</p>
      </button>
    </div>
  </div>
</template>
