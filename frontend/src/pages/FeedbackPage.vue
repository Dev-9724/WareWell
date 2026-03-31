<template>
  <div class="feedback-page">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">Learning Signal</p>
        <h1>Feedback Input</h1>
        <p class="subtitle">
          Share quick feedback about the selected outfit so the system can support
          future ranking improvements and adaptive recommendation refinement.
        </p>
      </div>

      <div class="hero-badge">Adaptive Ranking</div>
    </section>

    <section class="form-card">
      <div class="card-header">
        <div>
          <h2>Selected Outfit Feedback</h2>
          <p>
            The selected outfit details are passed automatically from the recommendation page.
          </p>
        </div>

        <router-link class="back-link" to="/recommendations">
          Back to Recommendations
        </router-link>
      </div>

      <div class="selected-outfit-box">
        <div class="selected-header">
          <div>
            <span class="mini-label">Selected Outfit</span>
            <h3>{{ outfitLabel }}</h3>
          </div>
        </div>

        <div class="selected-meta">
          <div>
            <span>Occasion</span>
            <strong>{{ formattedOccasion }}</strong>
          </div>
          <div>
            <span>Outfit Reference</span>
            <strong>{{ resolvedOutfitId }}</strong>
          </div>
        </div>
      </div>

      <form class="feedback-form" @submit.prevent="handleSubmit">
        <div class="form-grid">
          <div class="form-group">
            <label for="occasion">Occasion</label>
            <select id="occasion" v-model="form.occasion">
              <option value="casual">Casual</option>
              <option value="office">Office</option>
              <option value="formal">Formal</option>
              <option value="party">Party</option>
            </select>
          </div>

          <div class="form-group">
            <label for="rating">Feedback Type</label>
            <select id="rating" v-model="form.rating">
              <option value="perfect">Perfect</option>
              <option value="okay">Okay</option>
              <option value="not_suitable">Not Suitable</option>
            </select>
          </div>

          <div class="form-group full-width">
            <label for="comment">Comment</label>
            <textarea
              id="comment"
              v-model="form.comment"
              rows="5"
              placeholder="Write a short reason for your feedback..."
            />
          </div>
        </div>

        <div v-if="errorMessage" class="message error-message">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="message success-message">
          {{ successMessage }}
        </div>

        <div class="action-row">
          <button class="submit-btn" type="submit" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Feedback' }}
          </button>

          <router-link class="secondary-btn" to="/explanations">
            Back to Explanation
          </router-link>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { submitFeedback } from '../services/api'

const route = useRoute()

const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const selectedOccasion = String(route.query.occasion || 'casual')
const selectedOutfitId = String(route.query.outfit_id || 'outfit-1').trim()
const selectedOutfitLabel = String(route.query.outfit_label || '').trim()

const form = reactive({
  occasion: selectedOccasion,
  rating: 'okay',
  comment: '',
})

const resolvedOutfitId = computed(() => {
  return selectedOutfitId || 'outfit-1'
})

const outfitLabel = computed(() => {
  if (selectedOutfitLabel) return selectedOutfitLabel
  return 'Generated outfit'
})

const formattedOccasion = computed(() => {
  const map = {
    casual: 'Casual',
    office: 'Office',
    formal: 'Formal',
    party: 'Party',
  }

  const key = String(form.occasion || '').toLowerCase()
  return map[key] || key
})

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!form.rating) {
    errorMessage.value = 'Please select a feedback type.'
    return
  }

  submitting.value = true

  try {
    await submitFeedback({
      outfit_id: resolvedOutfitId.value,
      rating: form.rating,
      occasion: form.occasion,
      comment: form.comment.trim(),
    })

    successMessage.value = 'Feedback submitted successfully.'
    form.comment = ''
    form.rating = 'okay'
  } catch (error) {
    console.error(error)
    errorMessage.value =
      error?.message || 'Something went wrong while submitting feedback.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.feedback-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.form-card {
  background: #ffffff;
  border: 1px solid #e3e8f2;
  border-radius: 24px;
  box-shadow: 0 12px 30px rgba(8, 18, 37, 0.04);
  padding: 28px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 10px;
  color: #1dd1a1;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-copy h1 {
  margin: 0 0 10px;
  color: #081225;
  font-size: 2rem;
}

.subtitle {
  margin: 0;
  color: #6a7790;
  line-height: 1.7;
}

.hero-badge {
  background: #eef5ff;
  color: #31507f;
  padding: 10px 14px;
  border-radius: 999px;
  font-weight: 700;
  white-space: nowrap;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.card-header h2 {
  margin: 0 0 6px;
  color: #081225;
}

.card-header p {
  margin: 0;
  color: #6a7790;
}

.back-link {
  text-decoration: none;
  background: #f7f9fc;
  color: #31507f;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid #dfe7f2;
  font-weight: 700;
}

.selected-outfit-box {
  margin-top: 20px;
  padding: 20px;
  border-radius: 20px;
  background: #f8fbff;
  border: 1px solid #e1e8f4;
}

.selected-header {
  margin-bottom: 16px;
}

.mini-label {
  display: inline-block;
  margin-bottom: 8px;
  color: #6a7790;
  font-size: 0.85rem;
  font-weight: 700;
}

.selected-header h3 {
  margin: 0;
  color: #081225;
  font-size: 1.3rem;
}

.selected-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.selected-meta div {
  background: #ffffff;
  border: 1px solid #e3e8f2;
  border-radius: 16px;
  padding: 14px;
  display: grid;
  gap: 6px;
}

.selected-meta span {
  color: #6a7790;
  font-size: 0.9rem;
}

.selected-meta strong {
  color: #081225;
}

.feedback-form {
  margin-top: 22px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px 18px;
}

.form-group {
  display: grid;
  gap: 8px;
}

.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  color: #081225;
  font-weight: 700;
}

.form-group select,
.form-group textarea {
  width: 100%;
  border: 1px solid #cfd9e8;
  border-radius: 16px;
  padding: 14px 16px;
  font-size: 15px;
  background: #ffffff;
  color: #081225;
  outline: none;
}

.form-group textarea {
  resize: vertical;
  min-height: 140px;
}

.message {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 600;
}

.error-message {
  background: #fff1f1;
  color: #9b1c1c;
  border: 1px solid #ffd4d4;
}

.success-message {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #bbf7d0;
}

.action-row {
  margin-top: 22px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.submit-btn,
.secondary-btn {
  min-height: 54px;
  padding: 0 20px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.submit-btn {
  border: none;
  background: #081225;
  color: white;
  cursor: pointer;
}

.secondary-btn {
  background: #eef4fb;
  color: #31507f;
  border: 1px solid #d7e0ec;
}

@media (max-width: 900px) {
  .hero-card,
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid,
  .selected-meta {
    grid-template-columns: 1fr;
  }
}
</style>