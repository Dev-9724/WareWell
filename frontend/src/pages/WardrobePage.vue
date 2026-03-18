<template>
  <div>
    <h1>Wardrobe</h1>
    <p>View all wardrobe items stored in the backend.</p>

    <div v-if="loading">Loading wardrobe items...</div>

    <div v-else-if="error" class="error-box">
      {{ error }}
    </div>

    <div v-else-if="items.length === 0">
      No wardrobe items found.
    </div>

    <div v-else class="wardrobe-grid">
      <div v-for="item in items" :key="item.id" class="item-card">
        <h3>{{ item.category }}</h3>
        <p><strong>Primary Colour:</strong> {{ item.colour_primary }}</p>
        <p><strong>Secondary Colour:</strong> {{ item.colour_secondary || 'None' }}</p>
        <p><strong>Formality:</strong> {{ item.formality_level }}</p>
        <p><strong>Season:</strong> {{ item.season?.join(', ') }}</p>
        <p><strong>Temperature:</strong> {{ item.temperature_min }} - {{ item.temperature_max }} °C</p>
        <p><strong>Rain Suitable:</strong> {{ item.rain_suitable ? 'Yes' : 'No' }}</p>
        <p><strong>Wear Count:</strong> {{ item.wear_count }}</p>
        <p><strong>Cost:</strong> £{{ item.cost }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getWardrobeItems } from '../services/api'

const items = ref([])
const loading = ref(true)
const error = ref('')

async function loadWardrobe() {
  loading.value = true
  error.value = ''

  try {
    const data = await getWardrobeItems()
    items.value = data
  } catch (err) {
    error.value = 'Failed to load wardrobe items.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadWardrobe()
})
</script>

<style scoped>
.wardrobe-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.item-card {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 16px;
}

.item-card h3 {
  margin-top: 0;
  text-transform: capitalize;
}

.error-box {
  margin-top: 16px;
  padding: 16px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  max-width: 420px;
}
</style>