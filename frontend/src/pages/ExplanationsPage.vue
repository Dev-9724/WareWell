<template>
  <div>
    <h1>Explanations</h1>
    <p>View human-readable explanations for recommended outfits.</p>

    <form class="explain-form" @submit.prevent="loadExplanations">
      <label>
        User ID
        <input v-model="userId" type="text" required />
      </label>

      <label>
        Occasion
        <select v-model="occasion">
          <option value="casual">Casual</option>
          <option value="smart-casual">Smart Casual</option>
          <option value="office">Office</option>
          <option value="formal">Formal</option>
          <option value="party">Party</option>
          <option value="gym">Gym</option>
        </select>
      </label>

      <button type="submit">Load Explanations</button>
    </form>

    <div v-if="loading" class="info-box">Loading explanations...</div>

    <div v-if="errorMessage" class="error-box">
      {{ errorMessage }}
    </div>

    <div v-if="result" class="explained-list">
      <div
        v-for="outfit in result.explained_outfits"
        :key="outfit.outfit_id"
        class="explanation-card"
      >
        <h2>Outfit #{{ outfit.outfit_id }}</h2>
        <p><strong>Score:</strong> {{ outfit.score }}</p>
        <p><strong>Summary:</strong> {{ outfit.summary }}</p>
        <p><strong>Weather Context:</strong> {{ outfit.weather_context }}</p>
        <p v-if="outfit.occasion_context"><strong>Occasion Context:</strong> {{ outfit.occasion_context }}</p>

        <div class="details-box">
          <h3>Details</h3>
          <ul>
            <li v-for="(detail, index) in outfit.details" :key="index">
              {{ detail }}
            </li>
          </ul>
        </div>

        <div class="items-box">
          <h3>Items</h3>
          <ul>
            <li v-for="item in outfit.items" :key="item.id">
              {{ item.category }} - {{ item.colour_primary }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getExplanations } from '../services/api'

const userId = ref('dev_mdx_user')
const occasion = ref('office')

const loading = ref(false)
const errorMessage = ref('')
const result = ref(null)

async function loadExplanations() {
  loading.value = true
  errorMessage.value = ''
  result.value = null

  try {
    result.value = await getExplanations(userId.value, occasion.value, 5, 20)
  } catch (err) {
    errorMessage.value = 'Failed to load explanations.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.explain-form {
  margin-top: 24px;
  display: grid;
  gap: 16px;
  max-width: 420px;
}

label {
  display: grid;
  gap: 6px;
  font-weight: 500;
}

input,
select,
button {
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
}

button {
  background: #111827;
  color: white;
  cursor: pointer;
}

.explained-list {
  margin-top: 28px;
  display: grid;
  gap: 20px;
}

.explanation-card {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 16px;
}

.details-box,
.items-box {
  margin-top: 14px;
}

.info-box,
.error-box {
  margin-top: 20px;
  padding: 16px;
  border-radius: 8px;
  max-width: 520px;
}

.info-box {
  background: #e0f2fe;
  color: #075985;
}

.error-box {
  background: #fee2e2;
  color: #991b1b;
}
</style>