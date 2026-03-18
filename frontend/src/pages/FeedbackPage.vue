<template>
  <div>
    <h1>Feedback</h1>
    <p>Submit user feedback for recommended outfits and view updated model weights.</p>

    <form class="feedback-form" @submit.prevent="handleSubmit">
      <label>
        User ID
        <input v-model="form.user_id" type="text" required />
      </label>

      <label>
        Outfit ID
        <input v-model.number="form.outfit_id" type="number" min="1" required />
      </label>

      <label>
        Rating
        <select v-model="form.rating" required>
          <option value="perfect">Perfect</option>
          <option value="okay">Okay</option>
          <option value="not_suitable">Not Suitable</option>
        </select>
      </label>

      <label>
        Occasion
        <select v-model="form.occasion">
          <option value="office">Office</option>
          <option value="casual">Casual</option>
          <option value="smart-casual">Smart Casual</option>
          <option value="formal">Formal</option>
          <option value="party">Party</option>
          <option value="gym">Gym</option>
        </select>
      </label>

      <button type="submit">Submit Feedback</button>
    </form>

    <div v-if="loading" class="info-box">
      Submitting feedback...
    </div>

    <div v-if="successMessage" class="success-box">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="error-box">
      {{ errorMessage }}
    </div>

    <div v-if="feedbackResult" class="result-card">
      <h2>Feedback Saved</h2>
      <p><strong>User ID:</strong> {{ feedbackResult.user_id }}</p>
      <p><strong>Outfit ID:</strong> {{ feedbackResult.outfit_id }}</p>
      <p><strong>Rating:</strong> {{ feedbackResult.rating }}</p>
      <p><strong>Occasion:</strong> {{ feedbackResult.occasion || 'None' }}</p>
      <p><strong>Timestamp:</strong> {{ feedbackResult.timestamp }}</p>

      <div class="weights-section">
        <div class="weight-card">
          <h3>Weights Before</h3>
          <p><strong>Weather Fit:</strong> {{ feedbackResult.weights_before.weather_fit }}</p>
          <p><strong>Formality Match:</strong> {{ feedbackResult.weights_before.formality_match }}</p>
          <p><strong>Colour Harmony:</strong> {{ feedbackResult.weights_before.colour_harmony }}</p>
          <p><strong>Usage Balance:</strong> {{ feedbackResult.weights_before.usage_balance }}</p>
          <p><strong>Comfort:</strong> {{ feedbackResult.weights_before.comfort }}</p>
        </div>

        <div class="weight-card">
          <h3>Weights After</h3>
          <p><strong>Weather Fit:</strong> {{ feedbackResult.weights_after.weather_fit }}</p>
          <p><strong>Formality Match:</strong> {{ feedbackResult.weights_after.formality_match }}</p>
          <p><strong>Colour Harmony:</strong> {{ feedbackResult.weights_after.colour_harmony }}</p>
          <p><strong>Usage Balance:</strong> {{ feedbackResult.weights_after.usage_balance }}</p>
          <p><strong>Comfort:</strong> {{ feedbackResult.weights_after.comfort }}</p>
        </div>
      </div>
    </div>

    <div class="weights-panel">
      <h2>Current Learned Weights</h2>

      <button class="secondary-btn" @click="loadWeights">Refresh Weights</button>

      <div v-if="weightsLoading" class="info-box">
        Loading current weights...
      </div>

      <div v-else-if="currentWeights" class="result-card">
        <p><strong>Weather Fit:</strong> {{ currentWeights.weights.weather_fit }}</p>
        <p><strong>Formality Match:</strong> {{ currentWeights.weights.formality_match }}</p>
        <p><strong>Colour Harmony:</strong> {{ currentWeights.weights.colour_harmony }}</p>
        <p><strong>Usage Balance:</strong> {{ currentWeights.weights.usage_balance }}</p>
        <p><strong>Comfort:</strong> {{ currentWeights.weights.comfort }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { submitFeedback, getCurrentWeights } from '../services/api'

const form = ref({
  user_id: 'dev_mdx_user',
  outfit_id: 1,
  rating: 'perfect',
  occasion: 'office',
})

const loading = ref(false)
const weightsLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const feedbackResult = ref(null)
const currentWeights = ref(null)

async function handleSubmit() {
  loading.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    const result = await submitFeedback(form.value)
    feedbackResult.value = result
    successMessage.value = 'Feedback submitted successfully.'

    await loadWeights()
  } catch (err) {
    errorMessage.value = 'Failed to submit feedback.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadWeights() {
  weightsLoading.value = true

  try {
    const data = await getCurrentWeights()
    currentWeights.value = data
  } catch (err) {
    console.error('Failed to load current weights.', err)
  } finally {
    weightsLoading.value = false
  }
}

onMounted(() => {
  loadWeights()
})
</script>

<style scoped>
.feedback-form {
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

.secondary-btn {
  margin-top: 12px;
  margin-bottom: 16px;
  background: #2563eb;
}

.secondary-btn:hover {
  background: #1d4ed8;
}

.success-box,
.error-box,
.info-box {
  margin-top: 20px;
  padding: 16px;
  border-radius: 8px;
  max-width: 520px;
}

.success-box {
  background: #dcfce7;
  color: #166534;
}

.error-box {
  background: #fee2e2;
  color: #991b1b;
}

.info-box {
  background: #e0f2fe;
  color: #075985;
}

.result-card {
  margin-top: 24px;
  padding: 20px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  max-width: 760px;
}

.weights-section {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.weight-card {
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.weights-panel {
  margin-top: 32px;
}
</style>