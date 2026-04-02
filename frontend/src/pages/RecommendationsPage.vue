<template>
  <div class="recommendations-page">
    <section class="hero-card">
      <div>
        <p class="eyebrow">Ranked Outfit Selection</p>
        <h1>Recommended Outfit</h1>
        <p class="subtitle">
          Generate a complete outfit from your wardrobe using context-aware filtering, compatibility
          checks, and multi-criteria ranking.
        </p>
      </div>
    </section>

    <section class="controls-card">
      <div class="controls-grid">
        <div class="field">
          <label for="occasion">Occasion</label>
          <select id="occasion" v-model="occasion">
            <option value="casual">Casual</option>
            <option value="office">Office</option>
            <option value="formal">Formal</option>
            <option value="party">Party</option>
          </select>
        </div>

        <div class="field">
          <label>Number of Recommendations</label>
          <input id="topK" v-model.number="topK" type="number" min="1" max="10" />
        </div>

        <div class="field">
          <label for="maxOutfits">Max Outfits</label>
          <input id="maxOutfits" v-model.number="maxOutfits" type="number" min="1" max="10" />
        </div>
      </div>

      <button class="primary-btn" :disabled="loading" @click="loadRecommendations">
        {{ loading ? 'Generating...' : 'Generate Recommendations' }}
      </button>
    </section>

    <section v-if="error" class="error-card">
      {{ error }}
    </section>

    <section v-if="result" class="summary-card">
      <div class="summary-grid">
        <div class="summary-box">
          <span>Valid Items</span>
          <strong>{{ result.valid_item_count ?? 0 }}</strong>
        </div>
        <div class="summary-box">
          <span>Rejected Items</span>
          <strong>{{ result.rejected_item_count ?? 0 }}</strong>
        </div>
        <div class="summary-box">
          <span>Returned Outfits</span>
          <strong>{{ result.returned_ranked_outfit_count ?? 0 }}</strong>
        </div>
      </div>
    </section>

    <section v-if="!loading && result?.ranked_outfits?.length" class="recommended-layout">
      <article class="featured-outfit-card">
        <div class="featured-header">
          <div>
            <p class="featured-label">Top Recommendation</p>
            <h2>Your Recommended Outfit</h2>
          </div>
        </div>

        <div class="outfit-grid">
          <div v-for="card in displayCards" :key="card.category" class="outfit-item-card">
            <div class="item-visual" :class="card.visualClass">
              <img v-if="card.image" :src="card.image" :alt="card.title" class="item-image" />
              <div v-else class="placeholder-block">
                {{ card.category }}
              </div>
            </div>

            <div class="item-info">
              <p class="item-category">{{ card.category }}</p>
              <h3>{{ card.title }}</h3>
              <p class="item-meta">{{ card.meta }}</p>
            </div>
          </div>
        </div>

        <div class="explanation-card">
          <div class="explanation-head">
            <h3>Why this outfit?</h3>
            <router-link class="details-link" to="/explanations"> Scoring Details </router-link>
          </div>

          <div class="reason-list">
            <div v-for="(reason, index) in explanationReasons" :key="index" class="reason-row">
              <span class="reason-dot" :class="`dot-${index % 3}`"></span>
              <span>{{ reason }}</span>
            </div>
          </div>
        </div>

        <div class="action-stack">
          <button class="save-btn" type="button">Save Outfit</button>
          <button class="ghost-btn" type="button" @click="loadRecommendations">
            Generate Another
          </button>
          <router-link
            class="feedback-btn"
            :to="{
              path: '/feedback',
              query: {
                occasion: result?.occasion_used || occasion,
                outfit_id: selectedOutfit?.raw?.id || `outfit-${selectedOutfitIndex + 1}`,
                outfit_label: getCompactSummary(selectedOutfit),
                score: formatScore(selectedOutfitScore),
              },
            }"
          >
            Give Feedback
          </router-link>
        </div>
      </article>

      <aside class="side-panel">
        <div class="context-card">
          <h3>Context Used</h3>
          <div class="context-list">
            <div>
              <span>Occasion</span>
              <strong>{{ formatOccasion(result.occasion_used || occasion) }}</strong>
            </div>
            <div>
              <span>Temperature</span>
              <strong>{{ weatherTemp }}</strong>
            </div>
            <div>
              <span>Season</span>
              <strong>{{ weatherSeason }}</strong>
            </div>
            <div>
              <span>Condition</span>
              <strong>{{ weatherCondition }}</strong>
            </div>
          </div>
        </div>

        <div class="all-outfits-card">
          <h3>Other Outfits</h3>

          <button
            v-for="(outfit, index) in normalizedOutfits"
            :key="index"
            class="ranked-outfit-btn"
            :class="{ active: index === selectedOutfitIndex }"
            @click="selectedOutfitIndex = index"
          >
            <div>
              <strong>Outfit {{ index + 1 }}</strong>
              <p>{{ getCompactSummary(outfit) }}</p>
            </div>
            <!-- <span>{{ formatScore(outfit.score) }}</span> -->
          </button>
        </div>
      </aside>
    </section>

    <section v-else-if="!loading && result && !result?.ranked_outfits?.length" class="empty-card">
      <h3>No complete outfit generated</h3>
      <p>
        Try changing the weather data, selecting another occasion, or adding more wardrobe items
        with compatible season and temperature ranges.
      </p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { getImageUrl, getRankedOutfits } from '../services/api'

const occasion = ref('casual')
const topK = ref(1)
const maxOutfits = ref(20)
const loading = ref(false)
const error = ref('')
const result = ref(null)
const selectedOutfitIndex = ref(0)

const normalizedOutfits = computed(() => {
  const outfits = Array.isArray(result.value?.ranked_outfits) ? result.value.ranked_outfits : []

  return outfits.map((outfit, index) => normalizeOutfit(outfit, index))
})

const selectedOutfit = computed(() => {
  return normalizedOutfits.value[selectedOutfitIndex.value] || null
})

const selectedOutfitScore = computed(() => {
  return selectedOutfit.value?.score ?? 0
})

const displayCards = computed(() => {
  const selected = selectedOutfit.value

  if (!selected) return []

  return ['Top', 'Bottom', 'Shoes', 'Outerwear'].map((category) => {
    const item = selected.itemsByCategory[category] || null

    return {
      category,
      title: item?.name || item?.category || `No ${category}`,
      meta: buildItemMeta(item),
      image: item?.image_url ? getImageUrl(item.image_url) : '',
      visualClass: getVisualClass(category),
    }
  })
})

const explanationReasons = computed(() => {
  const selected = selectedOutfit.value
  const weather = result.value?.weather_used || {}

  const temp = weather?.temperature
  const occasionText = formatOccasion(result.value?.occasion_used || occasion.value)

  const generated = [
    temp !== undefined && temp !== null
      ? `Suitable for ${temp}°C weather.`
      : 'Suitable for the current weather context.',
    `Matches ${occasionText.toLowerCase()} formality requirements.`,
    `Built using category compatibility and outfit ranking rules.`,
  ]

  const backendReasons = Array.isArray(selected?.raw?.explanations)
    ? selected.raw.explanations
    : Array.isArray(selected?.raw?.reasons)
      ? selected.raw.reasons
      : []

  const readableBackendReasons = backendReasons
    .map((entry) => {
      if (typeof entry === 'string') return entry
      if (entry?.message) return entry.message
      if (entry?.reason) return entry.reason
      return null
    })
    .filter(Boolean)

  const merged = [...readableBackendReasons, ...generated]

  return [...new Set(merged)].slice(0, 4)
})

const weatherTemp = computed(() => {
  const value = result.value?.weather_used?.temperature
  return value === undefined || value === null ? '—' : `${value}°C`
})

const weatherSeason = computed(() => {
  const value = result.value?.weather_used?.season
  return value ? capitalize(value) : '—'
})

const weatherCondition = computed(() => {
  return result.value?.weather_used?.condition || '—'
})

function capitalize(value) {
  const text = String(value || '')
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : ''
}

function formatOccasion(value) {
  if (!value) return 'Casual'

  const map = {
    casual: 'Casual',
    office: 'Office',
    formal: 'Formal',
    party: 'Party',
  }

  return map[String(value).toLowerCase()] || capitalize(value)
}

function formatScore(value) {
  const num = Number(value || 0)
  return num.toFixed(2)
}

function getVisualClass(category) {
  const map = {
    Top: 'visual-top',
    Bottom: 'visual-bottom',
    Shoes: 'visual-shoes',
    Outerwear: 'visual-outerwear',
  }

  return map[category] || ''
}

function buildItemMeta(item) {
  if (!item) return 'Item unavailable'

  const parts = []

  if (item.colour_primary) parts.push(item.colour_primary)
  if (item.occasion) parts.push(item.occasion)
  if (Array.isArray(item.season) && item.season.length) {
    parts.push(item.season.join(', '))
  }

  return parts.join(' • ') || 'Wardrobe item'
}

function getCompactSummary(outfit) {
  const values = ['Top', 'Bottom', 'Shoes', 'Outerwear']
    .map((category) => outfit.itemsByCategory[category]?.name || null)
    .filter(Boolean)

  if (!values.length) return 'Generated outfit'

  return values.join(' • ')
}

function normalizeOutfit(outfit, index) {
  const rawItems = extractRawItems(outfit)
  const itemsByCategory = {
    Top: null,
    Bottom: null,
    Shoes: null,
    Outerwear: null,
  }

  rawItems.forEach((item) => {
    const category = normalizeCategory(item?.category)
    if (category && !itemsByCategory[category]) {
      itemsByCategory[category] = item
    }
  })

  return {
    index,
    score:
      outfit?.total_score ?? outfit?.final_score ?? outfit?.score ?? outfit?.weighted_score ?? 0,
    raw: outfit,
    itemsByCategory,
  }
}

function extractRawItems(outfit) {
  if (!outfit || typeof outfit !== 'object') return []

  if (Array.isArray(outfit.items)) return outfit.items
  if (Array.isArray(outfit.outfit_items)) return outfit.outfit_items
  if (Array.isArray(outfit.outfit)) return outfit.outfit

  const bucketCandidates = ['top', 'bottom', 'shoes', 'outerwear', 'accessory']
  const bucketItems = bucketCandidates
    .map((key) => outfit[key])
    .filter(Boolean)
    .flatMap((entry) => (Array.isArray(entry) ? entry : [entry]))

  if (bucketItems.length) return bucketItems

  return []
}

function normalizeCategory(value) {
  const category = String(value || '').toLowerCase()

  if (category === 'top' || category === 'tops') return 'Top'
  if (category === 'bottom' || category === 'bottoms') return 'Bottom'
  if (category === 'shoes' || category === 'shoe') return 'Shoes'
  if (category === 'outerwear') return 'Outerwear'
  if (category === 'accessory' || category === 'accessories') return 'Accessory'

  return null
}

async function loadRecommendations() {
  loading.value = true
  error.value = ''
  result.value = null
  selectedOutfitIndex.value = 0

  try {
    result.value = await getRankedOutfits(occasion.value, topK.value, maxOutfits.value)
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to generate recommendations.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recommendations-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.controls-card,
.summary-card,
.featured-outfit-card,
.context-card,
.all-outfits-card,
.error-card,
.empty-card {
  background: #ffffff;
  border: 1px solid #e3e8f2;
  border-radius: 24px;
  box-shadow: 0 12px 30px rgba(8, 18, 37, 0.04);
}

.hero-card,
.controls-card,
.summary-card,
.error-card,
.empty-card {
  padding: 24px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #1dd1a1;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-card h1 {
  margin: 0 0 10px;
  color: #081225;
  font-size: 2rem;
}

.subtitle {
  margin: 0;
  color: #6a7790;
  line-height: 1.7;
  max-width: 760px;
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
}

.field label {
  font-weight: 700;
  color: #081225;
}

.field input,
.field select {
  min-height: 52px;
  padding: 12px 14px;
  border: 1px solid #d7e0ec;
  border-radius: 14px;
  font-size: 15px;
}

.primary-btn,
.save-btn,
.ghost-btn,
.feedback-btn {
  min-height: 54px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
}

.primary-btn {
  margin-top: 18px;
  border: none;
  background: #081225;
  color: white;
  padding: 0 18px;
  cursor: pointer;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.summary-box {
  padding: 18px;
  border-radius: 18px;
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  display: grid;
  gap: 8px;
}

.summary-box span {
  color: #6a7790;
}

.summary-box strong {
  color: #081225;
  font-size: 1.6rem;
}

.recommended-layout {
  display: grid;
  grid-template-columns: 1.7fr 0.9fr;
  gap: 24px;
  align-items: start;
}

.featured-outfit-card,
.context-card,
.all-outfits-card {
  padding: 24px;
}

.featured-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 22px;
}

.featured-label {
  margin: 0 0 8px;
  color: #6a7790;
  font-weight: 700;
}

.featured-header h2 {
  margin: 0;
  color: #081225;
}

.score-pill {
  background: #081225;
  color: white;
  border-radius: 999px;
  padding: 12px 16px;
  font-weight: 700;
  white-space: nowrap;
}

.outfit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.outfit-item-card {
  background: #fafbfd;
  border: 1px solid #e7edf5;
  border-radius: 22px;
  padding: 18px;
}

.item-visual {
  height: 180px;
  border-radius: 18px;
  overflow: hidden;
  margin-bottom: 16px;
  display: grid;
  place-items: center;
}

.visual-top {
  background: linear-gradient(180deg, #5a95df 0%, #4d86cf 100%);
}

.visual-bottom {
  background: linear-gradient(180deg, #1e2a3e 0%, #1b2435 100%);
}

.visual-shoes {
  background: linear-gradient(180deg, #a94f0c 0%, #994607 100%);
}

.visual-outerwear {
  background: linear-gradient(180deg, #848b9b 0%, #737b8c 100%);
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-block {
  color: white;
  font-weight: 800;
  font-size: 1.15rem;
}

.item-category {
  margin: 0 0 8px;
  color: #6a7790;
  font-size: 0.95rem;
}

.item-info h3 {
  margin: 0 0 6px;
  color: #081225;
  font-size: 1.5rem;
}

.item-meta {
  margin: 0;
  color: #5f6d86;
  line-height: 1.5;
}

.explanation-card {
  margin-top: 24px;
  padding: 22px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid #e7edf5;
  box-shadow: 0 10px 24px rgba(8, 18, 37, 0.04);
}

.explanation-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 18px;
}

.explanation-head h3 {
  margin: 0;
  color: #081225;
  font-size: 1.8rem;
}

.details-link {
  color: #49b44a;
  text-decoration: none;
  font-weight: 700;
}

.reason-list {
  display: grid;
  gap: 16px;
}

.reason-row {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #081225;
  font-size: 1.1rem;
}

.reason-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-0 {
  background: #4caf50;
}

.dot-1 {
  background: #f6b347;
}

.dot-2 {
  background: #4f8ddf;
}

.action-stack {
  display: grid;
  gap: 14px;
  margin-top: 24px;
}

.save-btn {
  border: none;
  background: #4caf50;
  color: white;
  cursor: pointer;
}

.ghost-btn {
  border: 2px solid #4caf50;
  background: transparent;
  color: #4caf50;
  cursor: pointer;
}

.feedback-btn {
  display: grid;
  place-items: center;
  background: #f7f9fc;
  color: #081225;
  text-decoration: none;
  border: 1px solid #e7edf5;
}

.side-panel {
  display: grid;
  gap: 24px;
}

.context-card h3,
.all-outfits-card h3 {
  margin: 0 0 18px;
  color: #081225;
}

.context-list {
  display: grid;
  gap: 14px;
}

.context-list div {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 14px;
  border-radius: 14px;
  background: #f7f9fc;
  border: 1px solid #e7edf5;
}

.context-list span {
  color: #6a7790;
}

.context-list strong {
  color: #081225;
}

.ranked-outfit-btn {
  width: 100%;
  border: 1px solid #e7edf5;
  background: #f7f9fc;
  border-radius: 16px;
  padding: 14px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  cursor: pointer;
  margin-bottom: 12px;
}

.ranked-outfit-btn strong {
  display: block;
  color: #081225;
  margin-bottom: 4px;
}

.ranked-outfit-btn p {
  margin: 0;
  color: #6a7790;
  font-size: 0.92rem;
  line-height: 1.45;
}

.ranked-outfit-btn span {
  font-weight: 700;
  color: #081225;
}

.ranked-outfit-btn.active {
  border-color: #081225;
  background: #eef3fb;
}

.error-card {
  background: #fff1f1;
  color: #9b1c1c;
}

.empty-card h3 {
  margin: 0 0 10px;
  color: #081225;
}

.empty-card p {
  margin: 0;
  color: #6a7790;
  line-height: 1.6;
}

@media (max-width: 1100px) {
  .recommended-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .controls-grid,
  .summary-grid,
  .outfit-grid {
    grid-template-columns: 1fr;
  }

  .featured-header,
  .explanation-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
