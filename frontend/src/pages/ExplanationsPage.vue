<template>
  <div class="explanations-page">
    <section class="controls-card">
      <div class="controls-header">
        <div>
          <p class="eyebrow">Explainable Recommendation</p>
          <h1>Outfit Explanations</h1>
          <p class="subtitle">
            Generate a visual explanation for ranked outfits using score contributions,
            context details, and confidence indicators.
          </p>
        </div>

        <button class="primary-btn" :disabled="loading" @click="loadExplanations">
          {{ loading ? 'Generating...' : 'Generate Explanations' }}
        </button>
      </div>

      <div class="controls-grid">
        <div class="field">
          <label for="occasion">Occasion</label>
          <select id="occasion" v-model="occasion">
            <option value="office">Office</option>
            <option value="casual">Casual</option>
            <option value="formal">Formal</option>
            <option value="party">Party</option>
          </select>
        </div>

        <div class="field">
          <label>Number of Recommendations</label>
          <input id="topK" v-model.number="topK" type="number" min="1" max="20" />
        </div>

        <div class="field">
          <label for="maxOutfits">Max Outfits</label>
          <input
            id="maxOutfits"
            v-model.number="maxOutfits"
            type="number"
            min="1"
            max="100"
          />
        </div>
      </div>
    </section>

    <section v-if="error" class="error-card">
      <h3>Unable to load explanations</h3>
      <p>{{ error }}</p>
    </section>

    <section v-if="loading" class="loading-card">
      <p>Generating recommendation explanations...</p>
    </section>

    <template v-if="explanations.length">
      <article
        v-for="(explanation, index) in explanations"
        :key="explanation.outfit_id || index"
        class="explanation-layout"
      >
        <div class="left-column">
          <section class="score-hero">
            <div class="score-icon">◎</div>
            <div>
              <p class="section-label light">Overall Match Score</p>
              <h2>{{ getScorePercent(explanation) }}%</h2>
              <p>{{ getRecommendationLabel(getScorePercent(explanation)) }}</p>
            </div>
          </section>

          <section class="breakdown-card">
            <h3>Algorithm Breakdown</h3>

            <div
              v-for="card in getBreakdownCards(explanation)"
              :key="card.key"
              class="breakdown-row"
            >
              <div class="breakdown-header">
                <div class="breakdown-title-wrap">
                  <span class="breakdown-icon" :class="'breakdown-icon--' + card.key">
                    {{ getIcon(card.key) }}
                  </span>
                  <div>
                    <h4>{{ card.label }}</h4>
                    <p>{{ card.description }}</p>
                  </div>
                </div>
                <strong>{{ card.percent }}%</strong>
              </div>

              <div class="bar-track">
                <div
                  class="bar-fill"
                  :class="'bar-fill--' + card.key"
                  :style="{ width: card.percent + '%' }"
                ></div>
              </div>
            </div>
          </section>
        </div>

        <div class="right-column">
          <section class="summary-card">
            <div class="card-heading">
              <p class="section-label">Recommendation Summary</p>
              <h3>Explained Outfit {{ index + 1 }}</h3>
            </div>

            <p class="summary-text">{{ explanation.summary }}</p>
            <p class="context-line">{{ explanation.weather_context }}</p>
            <p v-if="explanation.occasion_context" class="context-line">
              {{ explanation.occasion_context }}
            </p>
          </section>

          <section class="items-card">
            <div class="card-heading">
              <p class="section-label">Selected Items</p>
            </div>

            <div class="item-grid">
              <div
                v-for="(item, itemIndex) in explanation.items || []"
                :key="item.id || itemIndex"
                class="item-chip"
              >
                {{ getItemDisplayName(item) }}
              </div>
            </div>
          </section>

          <section class="params-card">
            <div class="card-heading">
              <p class="section-label">Model Parameters</p>
              <h3>Context Inputs</h3>
            </div>

            <div class="param-row">
              <span>Temperature Range</span>
              <strong>{{ explanation.model_parameters?.temperature_range || 'Not available' }}</strong>
            </div>
            <div class="param-row">
              <span>Weather Condition</span>
              <strong>{{ explanation.model_parameters?.weather_condition || 'Unknown' }}</strong>
            </div>
            <div class="param-row">
              <span>Occasion</span>
              <strong>{{ explanation.model_parameters?.occasion || capitalize(occasion) }}</strong>
            </div>
            <div class="param-row">
              <span>Season</span>
              <strong>{{ explanation.model_parameters?.season || 'Not specified' }}</strong>
            </div>
          </section>

          <section class="confidence-card">
            <div class="card-heading">
              <p class="section-label">Confidence Indicators</p>
            </div>

            <ul class="confidence-list">
              <li
                v-for="(item, confidenceIndex) in explanation.confidence_indicators || []"
                :key="confidenceIndex"
              >
                <span class="tick">✓</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </section>

          <section class="note-card">
            <p>
              This recommendation explanation presents score contributions, contextual
              reasoning, and confidence indicators to support transparent outfit selection.
            </p>
          </section>
        </div>
      </article>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getExplanations } from '../services/api'

const occasion = ref('formal')
const topK = ref(5)
const maxOutfits = ref(20)
const loading = ref(false)
const error = ref('')
const explanations = ref([])

function capitalize(value) {
  if (!value) return ''
  return value.charAt(0).toUpperCase() + value.slice(1)
}

function getScorePercent(explanation) {
  if (typeof explanation?.score_percentage === 'number') {
    return Math.round(explanation.score_percentage)
  }
  return Math.round((Number(explanation?.score || 0)) * 100)
}

function getRecommendationLabel(percent) {
  const score = Number(percent || 0)
  if (score >= 90) return 'Excellent recommendation'
  if (score >= 80) return 'Very good recommendation'
  if (score >= 65) return 'Good recommendation'
  if (score >= 50) return 'Moderate recommendation'
  return 'Needs improvement'
}

function getItemDisplayName(item) {
  if (!item) return 'Wardrobe Item'

  const parts = []
  if (item.colour_primary) parts.push(item.colour_primary)
  if (item.category) parts.push(item.category)

  return parts.length ? parts.join(' ') : item.name || 'Wardrobe Item'
}

function getIcon(key) {
  const icons = {
    weather_fit: '⟡',
    formality_match: '✦',
    colour_harmony: '◉',
    usage_balance: '↺',
    comfort: '☁',
  }
  return icons[key] || '•'
}

function getBreakdownCards(explanation) {
  if (Array.isArray(explanation?.breakdown_cards) && explanation.breakdown_cards.length) {
    return explanation.breakdown_cards
  }

  const scoreBreakdown = explanation?.score_breakdown || {}

  const labelMap = {
    weather_fit: 'Weather Compatibility',
    formality_match: 'Formality Match',
    colour_harmony: 'Colour Harmony',
    usage_balance: 'Wardrobe Balance',
    comfort: 'Comfort',
  }

  const descriptionMap = {
    weather_fit: 'Suitability for the current temperature and weather conditions.',
    formality_match: 'How well the outfit matches the selected occasion.',
    colour_harmony: 'How visually consistent the outfit colours are together.',
    usage_balance: 'How well the outfit supports balanced wardrobe usage.',
    comfort: 'Estimated comfort level for the current context.',
  }

  return Object.entries(scoreBreakdown).map(([key, value]) => {
    const score = Number(value || 0)
    return {
      key,
      label: labelMap[key] || key,
      percent: Math.round(score * 100),
      description: descriptionMap[key] || 'Score contribution.',
    }
  })
}

async function loadExplanations() {
  loading.value = true
  error.value = ''

  try {
    const response = await getExplanations(occasion.value, topK.value, maxOutfits.value)
    console.log('Explanation API response:', response)

    if (Array.isArray(response)) {
      explanations.value = response
    } else if (Array.isArray(response?.explained_outfits)) {
      explanations.value = response.explained_outfits
    } else if (Array.isArray(response?.explanations)) {
      explanations.value = response.explanations
    } else {
      explanations.value = []
      error.value = 'No explained outfits were returned by the API.'
    }
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to generate explanations.'
    explanations.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadExplanations()
})
</script>

<style scoped>
.explanations-page {
  display: grid;
  gap: 24px;
}

.controls-card,
.error-card,
.loading-card,
.score-hero,
.breakdown-card,
.summary-card,
.items-card,
.params-card,
.confidence-card,
.note-card {
  background: #ffffff;
  border: 1px solid #e8edf5;
  border-radius: 24px;
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
}

.controls-card,
.error-card,
.loading-card,
.breakdown-card,
.summary-card,
.items-card,
.params-card,
.confidence-card,
.note-card {
  padding: 24px;
}

.controls-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.eyebrow,
.section-label {
  margin: 0 0 8px;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
}

.section-label.light {
  color: rgba(255, 255, 255, 0.85);
}

.controls-header h1 {
  margin: 0 0 10px;
  font-size: clamp(2rem, 4vw, 2.8rem);
  color: #0f172a;
}

.subtitle,
.error-card p,
.loading-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.field {
  display: grid;
  gap: 8px;
}

.field label {
  font-weight: 700;
  color: #1e293b;
}

.field input,
.field select {
  width: 100%;
  padding: 13px 14px;
  border: 1px solid #dbe3ef;
  border-radius: 14px;
  background: #f8fafc;
  color: #0f172a;
  font-size: 0.96rem;
}

.primary-btn {
  border: none;
  border-radius: 16px;
  padding: 14px 20px;
  font-weight: 800;
  font-size: 0.96rem;
  cursor: pointer;
  background: #0f172a;
  color: #ffffff;
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.18);
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.explanation-layout {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 22px;
  align-items: start;
}

.left-column,
.right-column {
  display: grid;
  gap: 20px;
}

.score-hero {
  padding: 28px;
  background: linear-gradient(135deg, #41a646 0%, #4fb24d 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 18px;
}

.score-icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.14);
  font-size: 1.5rem;
  font-weight: 800;
}

.score-hero h2 {
  margin: 0;
  font-size: clamp(3rem, 6vw, 4.6rem);
  line-height: 1;
}

.score-hero p:last-child {
  margin: 10px 0 0;
  font-size: 1.1rem;
}

.breakdown-card h3,
.card-heading h3 {
  margin: 0 0 18px;
  color: #0f172a;
  font-size: 1.5rem;
}

.breakdown-row + .breakdown-row {
  margin-top: 18px;
}

.breakdown-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 10px;
}

.breakdown-title-wrap {
  display: flex;
  gap: 14px;
}

.breakdown-title-wrap h4 {
  margin: 0 0 6px;
  font-size: 1.2rem;
  color: #0f172a;
}

.breakdown-title-wrap p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

.breakdown-header strong {
  font-size: 1.2rem;
  color: #41a646;
}

.breakdown-icon {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-weight: 800;
  flex-shrink: 0;
}

.breakdown-icon--weather_fit {
  background: #edf7ed;
  color: #41a646;
}

.breakdown-icon--formality_match {
  background: #fff5e9;
  color: #f1aa3c;
}

.breakdown-icon--colour_harmony {
  background: #eef5ff;
  color: #4d8dde;
}

.breakdown-icon--usage_balance {
  background: #f3f4f6;
  color: #7c3aed;
}

.breakdown-icon--comfort {
  background: #f4f1ff;
  color: #8b5e57;
}

.bar-track {
  width: 100%;
  height: 12px;
  background: #edf2f7;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-fill--weather_fit {
  background: #41a646;
}

.bar-fill--formality_match {
  background: #f1aa3c;
}

.bar-fill--colour_harmony {
  background: #4d8dde;
}

.bar-fill--usage_balance {
  background: #7c3aed;
}

.bar-fill--comfort {
  background: #8b5e57;
}

.summary-text {
  margin: 0 0 14px;
  color: #0f172a;
  font-size: 1.08rem;
  line-height: 1.8;
}

.context-line {
  margin: 0 0 8px;
  color: #64748b;
  line-height: 1.7;
}

.item-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.item-chip {
  padding: 16px 14px;
  background: #f8fafc;
  border: 1px solid #e7eef6;
  border-radius: 18px;
  text-align: center;
  color: #0f172a;
  font-weight: 700;
}

.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #edf2f7;
}

.param-row:last-child {
  border-bottom: none;
}

.param-row span {
  color: #64748b;
}

.param-row strong {
  color: #0f172a;
}

.confidence-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 14px;
}

.confidence-list li {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  color: #0f172a;
  line-height: 1.7;
}

.tick {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: #edf7ed;
  color: #41a646;
  font-weight: 800;
  flex-shrink: 0;
}

.note-card {
  background: #4d8dde;
  color: #ffffff;
}

.note-card p {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.8;
}

.error-card {
  background: #fff4f4;
  border-color: #ffd6d6;
}

.error-card h3 {
  margin: 0 0 8px;
  color: #991b1b;
}

.loading-card {
  text-align: center;
}

@media (max-width: 1100px) {
  .explanation-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .controls-grid,
  .item-grid {
    grid-template-columns: 1fr;
  }

  .controls-header {
    flex-direction: column;
  }

  .controls-card,
  .error-card,
  .loading-card,
  .score-hero,
  .breakdown-card,
  .summary-card,
  .items-card,
  .params-card,
  .confidence-card,
  .note-card {
    padding: 20px;
  }

  .breakdown-header {
    flex-direction: column;
  }
}
</style>