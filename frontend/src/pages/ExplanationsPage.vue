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
          <label for="topK">Number of Recommendations</label>
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

    <section v-else-if="!explanations.length && !error" class="loading-card">
      <p>No explanations available yet. Generate explanations to view outfit details.</p>
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
            <p class="context-line">{{ explanation.weather_context || getWeatherContextText() }}</p>
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
                :key="item.id || item._id || itemIndex"
                class="item-chip"
              >
                {{ getItemDisplayName(item) }}
              </div>
            </div>
          </section>

          <section class="params-card">
            <div class="card-heading">
              <p class="section-label">System Context</p>
              <h3>Context Inputs</h3>
            </div>

            <div class="param-row">
              <span>Temperature</span>
              <strong>{{ getContextInputs(explanation).temperature }}</strong>
            </div>
            <div class="param-row">
              <span>Weather Condition</span>
              <strong>{{ getContextInputs(explanation).condition }}</strong>
            </div>
            <div class="param-row">
              <span>Occasion</span>
              <strong>{{ getContextInputs(explanation).occasion }}</strong>
            </div>
            <div class="param-row">
              <span>Season</span>
              <strong>{{ getContextInputs(explanation).season }}</strong>
            </div>
          </section>

          <section class="confidence-card">
            <div class="card-heading">
              <p class="section-label">Confidence Indicators</p>
            </div>

            <ul class="confidence-list">
              <li
                v-for="(item, confidenceIndex) in getConfidenceIndicators(explanation)"
                :key="confidenceIndex"
              >
                <span class="tick">✓</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </section>

          <section class="note-card">
            <p>
              This explanation shows how constraint filtering, contextual suitability,
              and multi-criteria scoring contributed to the final outfit selection.
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
const weatherUsed = ref({})
const occasionUsed = ref('')
const targetFormalityUsed = ref(null)

function capitalize(value) {
  if (!value) return ''
  return value.charAt(0).toUpperCase() + value.slice(1)
}

function toDisplayText(value, fallback) {
  if (value === null || value === undefined || value === '') return fallback
  return String(value)
}

function formatTemperature(value) {
  const numericValue = Number(value)
  if (Number.isFinite(numericValue)) {
    return `${Math.round(numericValue)}°C`
  }
  return 'Not available'
}

function getSeasonFromDate() {
  const month = new Date().getMonth() + 1

  if ([12, 1, 2].includes(month)) return 'Winter'
  if ([3, 4, 5].includes(month)) return 'Spring'
  if ([6, 7, 8].includes(month)) return 'Summer'
  return 'Autumn'
}

function getScorePercent(explanation) {
  if (typeof explanation?.score_percentage === 'number') {
    return Math.round(explanation.score_percentage)
  }

  const numericScore = Number(explanation?.score || 0)
  return Math.round(numericScore * 100)
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
  if (!item) return 'Wardrobe item'

  const parts = []
  if (item.colour_primary) parts.push(capitalize(item.colour_primary))
  if (item.category) parts.push(capitalize(item.category))
  if (item.subcategory) parts.push(`(${capitalize(item.subcategory)})`)

  if (parts.length) {
    return parts.join(' ')
  }

  return item.name || item.title || 'Wardrobe item'
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

function getContextInputs(explanation) {
  const legacyParams = explanation?.model_parameters || {}

  return {
    temperature:
      legacyParams.temperature_range ||
      formatTemperature(weatherUsed.value?.temperature),
    condition:
      legacyParams.weather_condition ||
      toDisplayText(weatherUsed.value?.condition, 'Unknown'),
    occasion:
      legacyParams.occasion ||
      capitalize(occasionUsed.value || occasion.value) ||
      'Not specified',
    season:
      legacyParams.season ||
      toDisplayText(weatherUsed.value?.season, getSeasonFromDate()),
  }
}

function getWeatherContextText() {
  const city = toDisplayText(weatherUsed.value?.city, 'the selected city')
  const temperature = formatTemperature(weatherUsed.value?.temperature)
  const condition = toDisplayText(weatherUsed.value?.condition, 'unknown')

  return `The recommendation was generated for ${city} with temperature ${temperature} and condition ${condition}.`
}

function getConfidenceIndicators(explanation) {
  if (
    Array.isArray(explanation?.confidence_indicators) &&
    explanation.confidence_indicators.length
  ) {
    return explanation.confidence_indicators
  }

  const indicators = []
  const scorePercent = getScorePercent(explanation)
  const itemCount = Array.isArray(explanation?.items) ? explanation.items.length : 0
  const categoryText = explanation?.categories_used || 'selected categories'
  const condition = toDisplayText(weatherUsed.value?.condition, 'current weather conditions')
  const season = toDisplayText(weatherUsed.value?.season, getSeasonFromDate())
  const selectedOccasion = capitalize(occasionUsed.value || occasion.value) || 'selected occasion'

  indicators.push(`Overall match score: ${scorePercent}% based on multi-criteria ranking.`)

  if (itemCount > 0) {
    indicators.push(
      `This outfit includes ${itemCount} selected item${itemCount > 1 ? 's' : ''} that passed active constraints.`
    )
  } else {
    indicators.push('All selected items passed the active clothing constraints.')
  }

  indicators.push(
    `The recommendation remains suitable for ${condition.toLowerCase()} conditions in ${season.toLowerCase()}.`
  )
  indicators.push(
    `The outfit structure uses ${categoryText} to support a ${selectedOccasion.toLowerCase()} recommendation.`
  )

  if (targetFormalityUsed.value !== null && targetFormalityUsed.value !== undefined) {
    indicators.push(
      `Target formality ${Number(targetFormalityUsed.value).toFixed(1)} was applied during ranking.`
    )
  }

  return indicators
}

async function loadExplanations() {
  loading.value = true
  error.value = ''

  try {
    const response = await getExplanations(occasion.value, topK.value, maxOutfits.value)
    console.log('Explanation API response:', response)

    weatherUsed.value = response?.weather_used || {}
    occasionUsed.value = response?.occasion_used || occasion.value
    targetFormalityUsed.value = response?.target_formality_used ?? null

    if (Array.isArray(response)) {
      explanations.value = response
    } else if (Array.isArray(response?.explained_outfits)) {
      explanations.value = response.explained_outfits
    } else if (Array.isArray(response?.explanations)) {
      explanations.value = response.explanations
    } else {
      explanations.value = []
      error.value = response?.message || 'No explained outfits were returned by the API.'
    }
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to generate explanations.'
    explanations.value = []
    weatherUsed.value = {}
    occasionUsed.value = occasion.value
    targetFormalityUsed.value = null
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
.breakdown-card,
.summary-card,
.items-card,
.params-card,
.confidence-card,
.note-card {
  background: #ffffff;
  border: 1px solid #e7edf5;
  border-radius: 24px;
  box-shadow: none;
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
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
}

.section-label.light {
  color: rgba(255, 255, 255, 0.9);
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
  color: #0f172a;
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
  background: #0b1730;
  color: #ffffff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
}

.primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.error-card h3 {
  margin: 0 0 8px;
  color: #b91c1c;
}

.explanation-layout {
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(340px, 1.05fr);
  gap: 24px;
  align-items: start;
}

.left-column,
.right-column {
  display: grid;
  gap: 24px;
}

.score-hero {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 28px;
  border-radius: 24px;
  background: #4caf45;
  color: #ffffff;
  border: 1px solid #45a53f;
}

.score-icon {
  width: 68px;
  height: 68px;
  display: grid;
  place-items: center;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 1.8rem;
}

.score-hero h2 {
  margin: 0;
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  line-height: 1;
}

.score-hero p:last-child {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.95);
}

.breakdown-card h3,
.summary-card h3,
.params-card h3 {
  margin: 0;
  color: #0f172a;
}

.breakdown-card {
  display: grid;
  gap: 18px;
}

.breakdown-row {
  display: grid;
  gap: 12px;
}

.breakdown-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.breakdown-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.breakdown-title-wrap h4 {
  margin: 0 0 4px;
  color: #0f172a;
}

.breakdown-title-wrap p {
  margin: 0;
  color: #64748b;
  line-height: 1.55;
  font-size: 0.95rem;
}

.breakdown-header strong {
  color: #16a34a;
  font-weight: 800;
}

.breakdown-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  font-size: 1rem;
  flex-shrink: 0;
}

.breakdown-icon--weather_fit {
  background: #e7f7ea;
  color: #39a94b;
}

.breakdown-icon--formality_match {
  background: #fdf1df;
  color: #eea42b;
}

.breakdown-icon--colour_harmony {
  background: #e8f0fd;
  color: #4f89dd;
}

.breakdown-icon--usage_balance {
  background: #efe8ff;
  color: #7c3aed;
}

.breakdown-icon--comfort {
  background: #f3e7e2;
  color: #8b5e57;
}

.bar-track {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: #edf2f7;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-fill--weather_fit {
  background: #39a94b;
}

.bar-fill--formality_match {
  background: #eea42b;
}

.bar-fill--colour_harmony {
  background: #4f89dd;
}

.bar-fill--usage_balance {
  background: #7c3aed;
}

.bar-fill--comfort {
  background: #8b5e57;
}

.card-heading {
  margin-bottom: 16px;
}

.summary-text {
  margin: 0 0 14px;
  color: #0f172a;
  line-height: 1.7;
  font-size: 1rem;
}

.context-line {
  margin: 10px 0 0;
  color: #64748b;
  line-height: 1.6;
}

.item-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.item-chip {
  min-width: 160px;
  text-align: center;
  padding: 14px 18px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid #dbe3ef;
  color: #0f172a;
  font-weight: 700;
}

.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #eef2f7;
}

.param-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.param-row span {
  color: #64748b;
}

.param-row strong {
  color: #0f172a;
  text-align: right;
}

.confidence-card {
  min-height: 110px;
}

.confidence-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.confidence-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: #0f172a;
  line-height: 1.6;
}

.tick {
  color: #16a34a;
  font-weight: 800;
  margin-top: 1px;
}

.note-card {
  background: #4f89dd;
  border-color: #4f89dd;
}

.note-card p {
  margin: 0;
  color: #ffffff;
  line-height: 1.8;
}

@media (max-width: 980px) {
  .explanation-layout {
    grid-template-columns: 1fr;
  }

  .controls-grid {
    grid-template-columns: 1fr;
  }

  .controls-header {
    flex-direction: column;
  }
}

@media (max-width: 640px) {
  .controls-card,
  .error-card,
  .loading-card,
  .breakdown-card,
  .summary-card,
  .items-card,
  .params-card,
  .confidence-card,
  .note-card {
    padding: 18px;
  }

  .score-hero {
    padding: 22px;
  }

  .param-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .param-row strong {
    text-align: left;
  }

  .item-chip {
    min-width: 100%;
  }
}
</style>