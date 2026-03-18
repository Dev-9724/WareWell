<template>
  <div>
    <h1>WareWell Home</h1>
    <p>Welcome to the smart wardrobe recommendation system.</p>

    <section class="weather-section">
      <h2>Latest Weather Context</h2>

      <div v-if="loading">Loading weather...</div>

      <div v-else-if="error" class="error-box">
        {{ error }}
      </div>

      <div v-else-if="weather" class="weather-card">
        <p><strong>City:</strong> {{ weather.city }}</p>
        <p><strong>Temperature:</strong> {{ weather.temperature }} °C</p>
        <p><strong>Condition:</strong> {{ weather.condition }}</p>
        <p><strong>Humidity:</strong> {{ weather.humidity }}%</p>
        <p><strong>Wind:</strong> {{ weather.wind }}</p>
        <p><strong>Rain:</strong> {{ weather.rain }}</p>
        <p><strong>Source:</strong> {{ weather.source }}</p>
      </div>

      <div v-else>
        No weather data found yet.
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLatestWeather } from '../services/api'

const weather = ref(null)
const loading = ref(true)
const error = ref('')

async function loadWeather() {
  loading.value = true
  error.value = ''

  try {
    const data = await getLatestWeather()
    weather.value = data
  } catch (err) {
    error.value = 'Failed to load weather data from backend.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadWeather()
})
</script>

<style scoped>
.weather-section {
  margin-top: 32px;
}

.weather-card {
  margin-top: 16px;
  padding: 20px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  max-width: 420px;
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