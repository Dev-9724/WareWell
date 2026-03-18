<template>
  <div>
    <h1>Recommendations</h1>
    <p>Generate ranked outfit recommendations from the backend.</p>

    <form class="recommend-form" @submit.prevent="loadRecommendations">
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

      <label>
        Top K
        <input v-model.number="topK" type="number" min="1" max="10" />
      </label>

      <button type="submit">Get Recommendations</button>
    </form>

    <div v-if="loading">Loading recommendations...</div>

    <div v-else-if="errorMessage" class="error-box">
      {{ errorMessage }}
    </div>

    <div v-else-if="result" class="result-section">
      <div class="summary-card">
        <h2>Recommendation Summary</h2>
        <p><strong>City:</strong> {{ result.weather_used.city }}</p>
        <p><strong>Temperature:</strong> {{ result.weather_used.temperature }} °C</p>
        <p><strong>Condition:</strong> {{ result.weather_used.condition }}</p>
        <p><strong>Occasion:</strong> {{ result.occasion_used || 'None' }}</p>
        <p><strong>Target Formality:</strong> {{ result.target_formality_used }}</p>
        <p><strong>Valid Items:</strong> {{ result.valid_item_count }}</p>
        <p><strong>Rejected Items:</strong> {{ result.rejected_item_count }}</p>
        <p><strong>Generated Outfits:</strong> {{ result.generated_outfit_count }}</p>
        <p><strong>Returned Ranked Outfits:</strong> {{ result.returned_ranked_outfit_count }}</p>
      </div>

      <div class="weights-card">
        <h2>Weights Used</h2>
        <p><strong>Weather Fit:</strong> {{ result.weights_used.weather_fit }}</p>
        <p><strong>Formality Match:</strong> {{ result.weights_used.formality_match }}</p>
        <p><strong>Colour Harmony:</strong> {{ result.weights_used.colour_harmony }}</p>
        <p><strong>Usage Balance:</strong> {{ result.weights_used.usage_balance }}</p>
        <p><strong>Comfort:</strong> {{ result.weights_used.comfort }}</p>
      </div>

      <div class="outfits-section">
        <h2>Top Ranked Outfits</h2>

        <div
          v-for="outfit in result.ranked_outfits"
          :key="outfit.outfit_id"
          class="outfit-card"
        >
          <h3>Outfit #{{ outfit.outfit_id }}</h3>
          <p><strong>Total Score:</strong> {{ outfit.score }}</p>

          <div class="score-box">
            <p><strong>Weather Fit:</strong> {{ outfit.score_breakdown.weather_fit }}</p>
            <p><strong>Formality Match:</strong> {{ outfit.score_breakdown.formality_match }}</p>
            <p><strong>Colour Harmony:</strong> {{ outfit.score_breakdown.colour_harmony }}</p>
            <p><strong>Usage Balance:</strong> {{ outfit.score_breakdown.usage_balance }}</p>
            <p><strong>Comfort:</strong> {{ outfit.score_breakdown.comfort }}</p>
          </div>

          <div class="items-box">
            <h4>Items</h4>
            <ul>
              <li v-for="item in outfit.items" :key="item.id">
                <strong>{{ item.category }}</strong> —
                {{ item.colour_primary }}
                <span v-if="item.colour_secondary"> / {{ item.colour_secondary }}</span>,
                formality {{ item.formality_level }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="result.rejected_items?.length" class="rejected-section">
        <h2>Rejected Items</h2>
        <div
          v-for="item in result.rejected_items"
          :key="item.id"
          class="rejected-card"
        >
          <p><strong>Category:</strong> {{ item.category }}</p>
          <p><strong>Primary Colour:</strong> {{ item.colour_primary }}</p>
          <p><strong>Reasons:</strong> {{ item.reasons.join(', ') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getRankedOutfits } from '../services/api'

const userId = ref('dev_mdx_user')
const occasion = ref('office')
const topK = ref(5)

const loading = ref(false)
const errorMessage = ref('')
const result = ref(null)

async function loadRecommendations() {
  loading.value = true
  errorMessage.value = ''
  result.value = null

  try {
    const data = await getRankedOutfits(userId.value, occasion.value, topK.value, 20)
    result.value = data
  } catch (err) {
    errorMessage.value = 'Failed to load ranked recommendations.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recommend-form {
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

button:hover {
  background: #1f2937;
}

.result-section {
  margin-top: 32px;
  display: grid;
  gap: 24px;
}

.summary-card,
.weights-card,
.outfit-card,
.rejected-card {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 16px;
}

.score-box,
.items-box {
  margin-top: 12px;
}

.items-box ul {
  padding-left: 18px;
}

.error-box {
  margin-top: 20px;
  padding: 16px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  max-width: 500px;
}

.rejected-section {
  margin-top: 8px;
  display: grid;
  gap: 16px;
}
</style>