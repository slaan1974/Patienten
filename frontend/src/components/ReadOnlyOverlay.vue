<script setup>
defineProps({
  lockedByName: { type: String, default: 'Een andere gebruiker' },
})
</script>

<template>
  <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-4 flex items-center gap-3">
    <div class="text-2xl shrink-0">&#128274;</div>
    <div>
      <p class="font-semibold text-yellow-800">Alleen-lezen</p>
      <p class="text-yellow-700 text-sm">
        Dit record wordt momenteel bewerkt door <strong>{{ lockedByName }}</strong>.
      </p>
      <p class="text-yellow-600 text-xs mt-0.5">
        Je kunt de gegevens wel bekijken, maar niet wijzigen tot de lock is vrijgegeven.
      </p>
    </div>
  </div>
</template>
