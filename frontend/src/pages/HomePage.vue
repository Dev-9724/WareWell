<template>
  <div class="home-page">
    <section class="hero-card">
      <div>
        <p class="eyebrow">Today’s Wardrobe Assistant</p>
        <h1>Choose your context. Get a better outfit.</h1>
        <p class="hero-text">
          WareWell recommends outfits using live weather context, wardrobe constraints,
          multi-criteria scoring, explainable reasoning, and feedback learning.
        </p>
      </div>
      <div class="hero-badge">Hybrid Recommendation</div>
    </section>

    <section class="grid-two">
      <div class="panel-card">
        <div class="panel-header">
          <h2>Today’s Context</h2>
          <span class="tag">Start Here</span>
        </div>

        <div class="context-grid">
          <div class="info-chip">
            <span class="label">City</span>
            <strong>{{ weather?.city || 'Loading...' }}</strong>
          </div>
          <div class="info-chip">
            <span class="label">Condition</span>
            <strong>{{ weather?.condition || 'Loading...' }}</strong>
          </div>
          <div class="info-chip">
            <span class="label">Temperature</span>
            <strong>{{ weather?.temperature ?? '—' }} °C</strong>
          </div>
          <div class="info-chip">
            <span class="label">Humidity</span>
            <strong>{{ weather?.humidity ?? '—' }}%</strong>
          </div>
        </div>

        <form class="context-form" @submit.prevent="goToRecommendations">
          <label>
            Occasion
            <select v-model="occasion">
              <option value="casual">Casual</option>
              <option value="smart-casual">Smart Casual</option>
              <option value="office">Business / Office</option>
              <option value="formal">Formal Event</option>
              <option value="party">Party</option>
              <option value="gym">Gym</option>
            </select>
          </label>

          <div class="action-row">
            <button type="submit" class="primary-btn">
              Generate Outfit
            </button>

            <router-link class="secondary-btn" to="/wardrobe">
              Open Wardrobe
            </router-link>
          </div>
        </form>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h2>How it Works</h2>
          <span class="tag">System Pipeline</span>
        </div>

        <div class="pipeline">
          <div class="pipeline-step">1. Context Input</div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">2. Constraint Filtering</div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">3. Compatibility Check</div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">4. Scoring</div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">5. Best Outfit</div>
        </div>

        <div class="helper-box">
          <p>
            The system uses the current weather and your selected occasion to filter
            unsuitable items before ranking the best outfit combinations.
          </p>
        </div>
      </div>
    </section>

    <section class="panel-card quick-links">
      <div class="panel-header">
        <h2>Quick Access</h2>
        <span class="tag">Main Pages</span>
      </div>

      <div class="quick-grid">
        <router-link to="/wardrobe" class="quick-card">
          <h3>Wardrobe</h3>
          <p>Browse, search, and manage your clothing items.</p>
        </router-link>

        <router-link to="/add-item" class="quick-card">
          <h3>Add Item</h3>
          <p>Add a new clothing item to your wardrobe.</p>
        </router-link>

        <router-link to="/evaluation" class="quick-card">
          <h3>Evaluation</h3>
          <p>Review research and comparison metrics for the recommendation model.</p>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getLatestWeather } from '../services/api'

const router = useRouter()

const weather = ref(null)
const occasion = ref('office')

async function loadWeather() {
  try {
    weather.value = await getLatestWeather()
  } catch (error) {
    console.error('Failed to load weather:', error)
  }
}

function goToRecommendations() {
  router.push({
    path: '/recommendations',
    query: {
      occasion: occasion.value,
      auto: '1',
    },
  })
}

onMounted(() => {
  loadWeather()
})
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.panel-card,
.quick-card {
  background: white;
  border: 1px solid #e3e8f2;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(8, 18, 37, 0.04);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 10px;
  color: #1dd1a1;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.82rem;
  font-weight: 700;
}

.hero-card h1 {
  margin: 0 0 10px;
  font-size: clamp(2rem, 4vw, 3rem);
}

.hero-text {
  color: #6a7790;
  margin: 0;
  line-height: 1.6;
}

.hero-badge {
  white-space: nowrap;
  background: #081225;
  color: white;
  padding: 12px 16px;
  border-radius: 999px;
  font-weight: 700;
  height: fit-content;
}

.grid-two {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0;
}

.tag {
  background: #eef5ff;
  color: #31507f;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}

.context-grid,
.quick-grid {
  display: grid;
  gap: 14px;
}

.context-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 18px;
}

.info-chip {
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  color: #6a7790;
  font-size: 0.82rem;
}

.context-form {
  display: grid;
  gap: 14px;
}

.context-form label {
  display: grid;
  gap: 8px;
  font-weight: 600;
}

select,
button {
  padding: 12px;
  border: 1px solid #d6dfec;
  border-radius: 12px;
  font-size: 14px;
}

.action-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.primary-btn {
  background: #081225;
  color: white;
  border: none;
}

.secondary-btn {
  background: #eef5ff;
  color: #31507f;
  border: 1px solid #d6dfec;
}

.pipeline {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.pipeline-step {
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 12px;
  padding: 12px 14px;
  font-weight: 600;
}

.pipeline-arrow {
  color: #6a7790;
  font-weight: 700;
}

.helper-box {
  margin-top: 18px;
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 16px;
  color: #4b5870;
  line-height: 1.6;
}

.quick-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.quick-card {
  text-decoration: none;
  color: inherit;
}

.quick-card h3 {
  margin: 0 0 8px;
}

.quick-card p {
  margin: 0;
  color: #6a7790;
  line-height: 1.5;
}

@media (max-width: 1100px) {
  .grid-two,
  .quick-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 760px) {
  .context-grid {
    grid-template-columns: 1fr;
  }

  .hero-card,
  .panel-card,
  .quick-card {
    padding: 16px;
  }
}
</style>