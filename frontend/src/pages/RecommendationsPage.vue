<template>
  <div class="recommendations-page">
    <section class="hero-card">
      <p class="eyebrow">Ranked Outfit Selection</p>
      <h1>Recommended Outfit</h1>
      <p class="subtitle">
        Generate a complete outfit from your wardrobe using context-aware filtering, compatibility
        checks, and multi-criteria ranking.
      </p>
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
          <label for="topK">Number of Recommendations</label>
          <input id="topK" v-model.number="topK" type="number" min="1" max="20" />
        </div>

        <div class="field">
          <label for="maxOutfits">Max Outfits</label>
          <input id="maxOutfits" v-model.number="maxOutfits" type="number" min="1" max="100" />
        </div>
      </div>

      <div class="actions-row">
        <button class="primary-btn" :disabled="loading" @click="loadRecommendations">
          {{ loading ? 'Generating...' : 'Generate Recommendations' }}
        </button>
      </div>
    </section>

    <section v-if="error" class="status-card error-card">
      <h3>Unable to generate recommendations</h3>
      <p>{{ error }}</p>
    </section>

    <section v-else-if="message" class="status-card">
      <p>{{ message }}</p>
    </section>

    <section class="summary-grid">
      <article class="summary-item">
        <span>Valid Items</span>
        <strong>{{ validItemCount }}</strong>
      </article>

      <article class="summary-item">
        <span>Rejected Items</span>
        <strong>{{ rejectedItemCount }}</strong>
      </article>

      <article class="summary-item">
        <span>Returned Outfits</span>
        <strong>{{ rankedOutfits.length }}</strong>
      </article>
    </section>

    <section v-if="selectedOutfit" class="results-layout">
      <div class="results-main">
        <section class="outfit-card">
          <div class="section-heading">
            <div>
              <p class="section-label">Top Recommendation</p>
              <h2>Your Recommended Outfit</h2>
            </div>
          </div>

          <div class="outfit-grid">
            <article v-for="card in displayCards" :key="card.category" class="item-card">
              <div class="item-visual" :class="!card.image ? card.visualClass : ''">
                <img
                  v-if="card.image"
                  :src="card.image"
                  :alt="card.title"
                  class="item-image"
                  @error="handleImageError(card.category)"
                />
                <span v-else>{{ card.category }}</span>
              </div>

              <div class="item-body">
                <p class="item-category">{{ card.category }}</p>
                <h3>{{ card.title }}</h3>
                <p class="item-meta">{{ card.meta }}</p>
              </div>
            </article>
          </div>

          <section v-if="accessoryItems.length" class="accessories-card">
            <div class="accessories-header">
              <h3>Accessories</h3>
              <span class="accessories-badge">
                {{ accessoryItems.length }} item{{ accessoryItems.length > 1 ? 's' : '' }}
              </span>
            </div>

            <div class="accessory-chip-list">
              <div
                v-for="(item, index) in accessoryItems"
                :key="item._id || item.id || item.name || index"
                class="accessory-chip"
              >
                <span class="accessory-chip-title">
                  {{ item.name || item.title || 'Accessory' }}
                </span>
                <span class="accessory-chip-meta">
                  {{ buildItemMeta(item) }}
                </span>
              </div>
            </div>
          </section>

          <section class="reason-card">
            <div class="reason-header">
              <h3>Why this outfit?</h3>
              <router-link class="details-link" to="/explanations">Scoring Details</router-link>
            </div>

            <ul class="reason-list">
              <li v-for="(reason, index) in explanationReasons" :key="index">
                <span class="reason-dot" :class="'dot-' + (index % 4)"></span>
                <span>{{ reason }}</span>
              </li>
            </ul>
          </section>

          <div class="button-stack">
            <button class="save-btn" @click="saveOutfit">Save Outfit</button>
            <button class="outline-btn" @click="loadRecommendations">Generate Another</button>
            <button class="ghost-btn" @click="goToFeedback">Give Feedback</button>
          </div>
        </section>
      </div>

      <aside class="results-sidebar">
        <section class="context-card">
          <h3>Context Used</h3>

          <div class="context-row">
            <span>Occasion</span>
            <strong>{{ formatText(occasionUsed || occasion) }}</strong>
          </div>

          <div class="context-row">
            <span>Temperature</span>
            <strong>{{ formattedTemperature }}</strong>
          </div>

          <div class="context-row">
            <span>Season</span>
            <strong>{{ formattedSeason }}</strong>
          </div>

          <div class="context-row">
            <span>Condition</span>
            <strong>{{ formattedCondition }}</strong>
          </div>
        </section>

        <section class="other-card">
          <h3>Other Outfits</h3>

          <button
            v-for="outfit in otherOutfits"
            :key="outfit.index"
            class="other-outfit"
            :class="{ active: outfit.index === selectedOutfit.index }"
            @click="selectedIndex = outfit.index"
          >
            <div>
              <strong>Outfit {{ outfit.index + 1 }}</strong>
              <p>{{ getCompactSummary(outfit) }}</p>
            </div>
          </button>
        </section>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getRankedOutfits, getImageUrl } from '../services/api'

const router = useRouter()

const occasion = ref('casual')
const topK = ref(1)
const maxOutfits = ref(20)

const loading = ref(false)
const error = ref('')
const message = ref('')

const rankedOutfits = ref([])
const weatherUsed = ref({})
const occasionUsed = ref('')
const validItemCount = ref(0)
const rejectedItemCount = ref(0)
const selectedIndex = ref(0)

const brokenImages = ref({})

const selectedOutfit = computed(() => rankedOutfits.value[selectedIndex.value] || null)
const otherOutfits = computed(() => rankedOutfits.value)

function getRawImageValue(item) {
  if (!item) return ''

  return (
    item.image_url ||
    item.image_path ||
    item.image ||
    item.imageUrl ||
    item.imagePath ||
    item.photo_url ||
    item.photo ||
    ''
  )
}

function getResolvedImage(item, category) {
  if (!item) return ''

  if (brokenImages.value[category]) return ''

  const rawImage = getRawImageValue(item)
  return rawImage ? getImageUrl(rawImage) : ''
}

const displayCards = computed(() => {
  const selected = selectedOutfit.value
  if (!selected) return []

  return ['Top', 'Bottom', 'Shoes', 'Outerwear'].map((category) => {
    const item = selected.itemsByCategory[category] || null

    return {
      category,
      title: item?.name || item?.title || (item ? formatText(item.category) : `No ${category}`),
      meta: buildItemMeta(item),
      image: getResolvedImage(item, category),
      visualClass: getVisualClass(category),
    }
  })
})

const accessoryItems = computed(() => {
  const selected = selectedOutfit.value
  if (!selected) return []
  return Array.isArray(selected.accessoryItems) ? selected.accessoryItems : []
})

const explanationReasons = computed(() => {
  const selected = selectedOutfit.value
  if (!selected) return []

  const breakdown = selected.raw?.score_breakdown || {}
  const reasons = []

  if (Number(breakdown.weather_fit || 0) > 0) {
    reasons.push('Strong weather suitability for current conditions')
  }

  if (Number(breakdown.formality_match || 0) > 0) {
    reasons.push('Good occasion alignment for the selected context')
  }

  if (Number(breakdown.colour_harmony || 0) > 0) {
    reasons.push('Colour combination is visually consistent')
  }

  if (Number(breakdown.usage_balance || 0) > 0) {
    reasons.push('Supports sustainable wardrobe rotation')
  }

  if (Number(breakdown.comfort || 0) > 0) {
    reasons.push('Comfort is likely to be high in the current weather')
  }

  if (accessoryItems.value.length > 0) {
    reasons.push('Accessory selection helps complete the overall outfit composition')
  }

  if (!reasons.length) {
    reasons.push('This outfit achieved the strongest overall ranking score.')
  }

  return reasons
})

const formattedTemperature = computed(() => {
  const value = Number(weatherUsed.value?.temperature)
  return Number.isFinite(value) ? `${Math.round(value)}°C` : 'Not available'
})

const formattedSeason = computed(() => {
  return weatherUsed.value?.season ? formatText(weatherUsed.value.season) : 'Not specified'
})

const formattedCondition = computed(() => {
  return weatherUsed.value?.condition ? formatText(weatherUsed.value.condition) : 'Unknown'
})

function formatText(value) {
  if (!value) return ''
  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
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

  const values = []

  if (item.colour_primary) {
    values.push(formatText(item.colour_primary))
  } else if (item.color) {
    values.push(formatText(item.color))
  }

  const seasons = item.season || item.seasons
  if (Array.isArray(seasons) && seasons.length) {
    values.push(seasons.map((entry) => String(entry).toLowerCase()).join(', '))
  }

  return values.join(' • ') || 'Selected wardrobe item'
}

function normalizeCategory(category) {
  const value = String(category || '')
    .trim()
    .toLowerCase()

  if (value === 'top') return 'Top'
  if (value === 'bottom') return 'Bottom'
  if (value === 'shoes') return 'Shoes'
  if (value === 'outerwear') return 'Outerwear'
  if (value === 'accessory' || value === 'accessories') return 'Accessory'

  return ''
}

function extractRawItems(outfit) {
  if (Array.isArray(outfit?.items)) return outfit.items
  if (Array.isArray(outfit?.selected_items)) return outfit.selected_items
  return []
}

function normalizeOutfit(outfit, index) {
  const rawItems = extractRawItems(outfit)

  const itemsByCategory = {
    Top: null,
    Bottom: null,
    Shoes: null,
    Outerwear: null,
  }

  const accessoryItems = []

  rawItems.forEach((item) => {
    const category = normalizeCategory(item?.category)

    if (category === 'Accessory') {
      accessoryItems.push(item)
      return
    }

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
    accessoryItems,
  }
}

function getCompactSummary(outfit) {
  const mainItems = ['Top', 'Bottom', 'Shoes', 'Outerwear']
    .map((category) => outfit.itemsByCategory[category]?.name || null)
    .filter(Boolean)

  const accessories = Array.isArray(outfit.accessoryItems)
    ? outfit.accessoryItems.map((item) => item?.name || item?.title || null).filter(Boolean)
    : []

  const combined = [...mainItems, ...accessories]

  if (!combined.length) return 'Generated outfit'
  return combined.join(' • ')
}

function handleImageError(category) {
  brokenImages.value = {
    ...brokenImages.value,
    [category]: true,
  }
}

async function loadRecommendations() {
  loading.value = true
  error.value = ''
  message.value = ''
  brokenImages.value = {}

  try {
    const response = await getRankedOutfits(occasion.value, topK.value, maxOutfits.value)

    weatherUsed.value = response?.weather_used || {}
    occasionUsed.value = response?.occasion_used || occasion.value
    validItemCount.value = Number(response?.valid_item_count || 0)
    rejectedItemCount.value = Number(response?.rejected_item_count || 0)

    const rawRanked = Array.isArray(response?.ranked_outfits) ? response.ranked_outfits : []
    rankedOutfits.value = rawRanked.map((outfit, index) => normalizeOutfit(outfit, index))
    selectedIndex.value = 0

    if (!rankedOutfits.value.length) {
      message.value = response?.message || 'No ranked outfits were generated.'
    }
  } catch (err) {
    console.error(err)
    rankedOutfits.value = []
    selectedIndex.value = 0
    error.value = err?.message || 'Failed to generate outfit recommendations.'
  } finally {
    loading.value = false
  }
}

function saveOutfit() {
  if (!selectedOutfit.value) return
  alert('Outfit saved successfully.')
}

function goToFeedback() {
  if (!selectedOutfit.value) return

  const payload = {
    outfit_id: selectedOutfit.value.raw?.outfit_id || `outfit-${selectedOutfit.value.index + 1}`,
    outfit_name: `Generated outfit ${selectedOutfit.value.index + 1}`,
    occasion: occasionUsed.value || occasion.value,
    score: selectedOutfit.value.score,
    items: extractRawItems(selectedOutfit.value.raw),
  }

  router.push({
    path: '/feedback',
    query: {
      source: 'recommendation',
    },
    state: {
      selectedOutfit: payload,
    },
  })
}

onMounted(() => {
  loadRecommendations()
})
</script>

<style scoped>
.recommendations-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.controls-card,
.status-card,
.outfit-card,
.context-card,
.other-card,
.summary-item,
.reason-card,
.accessories-card {
  background: #ffffff;
  border: 1px solid #e7edf5;
  border-radius: 24px;
}

.hero-card,
.controls-card,
.status-card,
.outfit-card,
.context-card,
.other-card,
.reason-card,
.accessories-card {
  padding: 24px;
}

.eyebrow,
.section-label {
  margin: 0 0 8px;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #22c55e;
}

.hero-card h1,
.section-heading h2,
.context-card h3,
.other-card h3,
.reason-card h3,
.accessories-header h3 {
  margin: 0;
  color: #0f172a;
}

.subtitle,
.status-card p {
  margin: 12px 0 0;
  color: #64748b;
  line-height: 1.7;
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

.actions-row {
  margin-top: 18px;
}

.details-link {
  color: #49b44a;
  text-decoration: none;
  font-weight: 700;
}

.primary-btn,
.save-btn,
.outline-btn,
.ghost-btn {
  width: 100%;
  border-radius: 16px;
  padding: 14px 18px;
  font-weight: 800;
  font-size: 0.96rem;
  cursor: pointer;
}

.primary-btn {
  width: auto;
  border: none;
  background: #0b1730;
  color: #ffffff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.summary-item {
  padding: 18px 20px;
  display: grid;
  gap: 8px;
}

.summary-item span {
  color: #64748b;
}

.summary-item strong {
  font-size: 2rem;
  color: #0f172a;
}

.results-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(280px, 0.95fr);
  gap: 20px;
  align-items: start;
}

.results-main,
.results-sidebar {
  display: grid;
  gap: 20px;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.outfit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  align-items: stretch;
}

.item-card {
  border: 1px solid #dbe3ef;
  border-radius: 22px;
  overflow: hidden;
  background: #ffffff;
}

.item-visual {
  height: 210px;
  margin: 14px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  color: #ffffff;
  font-size: 1.15rem;
  font-weight: 800;
  text-align: center;
  overflow: hidden;
  background: #f8fafc;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.visual-top {
  background: linear-gradient(180deg, #6fa4ea 0%, #5b8fd3 100%);
}

.visual-bottom {
  background: linear-gradient(180deg, #22314f 0%, #1b2740 100%);
}

.visual-shoes {
  background: linear-gradient(180deg, #b85c08 0%, #a14f05 100%);
}

.visual-outerwear {
  background: linear-gradient(180deg, #9aa3b5 0%, #8b95a8 100%);
}

.item-body {
  padding: 0 20px 20px;
}

.item-category {
  margin: 0 0 8px;
  color: #64748b;
  font-size: 0.95rem;
}

.item-body h3 {
  margin: 0 0 8px;
  font-size: 1.1rem;
  color: #0f172a;
}

.item-meta {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

.accessories-card {
  margin-top: 20px;
}

.accessories-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.accessories-badge {
  padding: 8px 12px;
  border-radius: 999px;
  background: #eef4ff;
  color: #395b9a;
  font-weight: 700;
  font-size: 0.9rem;
}

.accessory-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.accessory-chip {
  min-width: 180px;
  max-width: 100%;
  display: grid;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid #dbe3ef;
}

.accessory-chip-title {
  color: #0f172a;
  font-weight: 700;
}

.accessory-chip-meta {
  color: #64748b;
  font-size: 0.92rem;
  line-height: 1.5;
}

.reason-card {
  margin-top: 20px;
}

.reason-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.reason-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.reason-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  color: #0f172a;
  line-height: 1.6;
}

.reason-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.dot-0 {
  background: #49b455;
}

.dot-1 {
  background: #f2b23c;
}

.dot-2 {
  background: #5c93e6;
}

.dot-3 {
  background: #49b455;
}

.button-stack {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.save-btn {
  border: none;
  background: #4caf45;
  color: #ffffff;
}

.outline-btn {
  border: 2px solid #4caf45;
  background: #ffffff;
  color: #4caf45;
}

.ghost-btn {
  border: 1px solid #dbe3ef;
  background: #f8fafc;
  color: #0f172a;
}

.context-card h3,
.other-card h3 {
  margin-bottom: 18px;
}

.context-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #eef2f7;
}

.context-row:last-child {
  border-bottom: none;
}

.context-row span {
  color: #64748b;
}

.context-row strong {
  color: #0f172a;
  text-align: right;
}

.other-card {
  display: grid;
  gap: 12px;
}

.other-outfit {
  width: 100%;
  border: 1px solid #dbe3ef;
  background: #f8fafc;
  border-radius: 18px;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  text-align: left;
  cursor: pointer;
}

.other-outfit.active {
  border-color: #0f172a;
  background: #eef4ff;
}

.other-outfit strong {
  display: block;
  color: #0f172a;
}

.other-outfit p {
  margin: 4px 0 0;
  color: #64748b;
  line-height: 1.5;
  font-size: 0.92rem;
}

.status-card {
  color: #475569;
}

.error-card h3 {
  margin: 0 0 8px;
  color: #b91c1c;
}

@media (max-width: 980px) {
  .results-layout {
    grid-template-columns: 1fr;
  }

  .controls-grid,
  .summary-grid,
  .outfit-grid {
    grid-template-columns: 1fr;
  }

  .primary-btn {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .hero-card,
  .controls-card,
  .status-card,
  .outfit-card,
  .context-card,
  .other-card,
  .reason-card,
  .accessories-card {
    padding: 18px;
  }

  .section-heading,
  .reason-header,
  .accessories-header,
  .context-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-visual {
    height: 180px;
  }

  .accessory-chip {
    min-width: 100%;
  }
}
</style>