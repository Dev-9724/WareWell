<template>
  <div class="recommendations-page">
    <section class="hero-card">
      <p class="eyebrow">Ranked Outfit Selection</p>
      <h1>Recommended Outfit</h1>
      <p class="subtitle">
        Generate a complete outfit from your wardrobe using context-aware filtering,
        compatibility checks, and multi-criteria ranking.
      </p>
    </section>

    <section class="controls-card">
      <div class="controls-grid">
        <div class="field-group">
          <label for="occasion">Occasion</label>
          <select id="occasion" v-model="occasion">
            <option value="casual">Casual</option>
            <option value="office">Office</option>
            <option value="formal">Formal</option>
            <option value="party">Party</option>
          </select>
        </div>

        <div class="field-group">
          <label for="topK">Number of Recommendations</label>
          <input id="topK" v-model.number="topK" type="number" min="1" max="20" />
        </div>

        <div class="field-group">
          <label for="maxOutfits">Max Outfits</label>
          <input id="maxOutfits" v-model.number="maxOutfits" type="number" min="1" max="100" />
        </div>

        <div class="field-group">
          <label for="location">Location</label>
          <input
            id="location"
            v-model.trim="location"
            type="text"
            placeholder="Enter city e.g. London"
          />
        </div>
      </div>

      <div class="actions-row">
        <button class="generate-btn" :disabled="isLoading" @click="generateRecommendations">
          {{ isLoading ? 'Generating...' : 'Generate Recommendations' }}
        </button>
      </div>

      <p v-if="statusMessage" class="status-message">
        {{ statusMessage }}
      </p>

      <p v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </p>
    </section>

    <section v-if="summaryCards.length" class="summary-grid">
      <article v-for="card in summaryCards" :key="card.label" class="summary-card">
        <p>{{ card.label }}</p>
        <h3>{{ card.value }}</h3>
      </article>
    </section>

    <section v-if="topRecommendation" class="results-layout">
      <div class="left-column">
        <article class="main-result-card">
          <p class="eyebrow">Top Recommendation</p>
          <h2>Your Recommended Outfit</h2>

          <div class="outfit-grid">
            <article
              v-for="(item, index) in displayedTopItems"
              :key="item._id || item.id || `${item.category}-${index}`"
              class="outfit-item-card"
            >
              <div class="item-image-frame">
                <img
                  v-if="resolveImage(item)"
                  :src="getImageUrl(resolveImage(item))"
                  :alt="item.name || item.category || 'Wardrobe item'"
                  class="item-image"
                />
                <div v-else class="item-placeholder">
                  {{ formatText(item.category || 'Item') }}
                </div>
              </div>

              <div class="item-details">
                <p class="item-category">{{ formatText(item.category) }}</p>
                <h4>{{ item.name || 'Unnamed Item' }}</h4>
                <p class="item-meta">
                  {{ item.color || 'Unknown colour' }}
                  <span v-if="formatSeasons(item)"> • {{ formatSeasons(item) }}</span>
                </p>
              </div>
            </article>
          </div>

          <div class="reason-box">
            <div class="reason-header">
              <h3>Why this outfit?</h3>
              <button class="scoring-link" type="button" @click="goToEvaluation">
                Scoring Details
              </button>
            </div>

            <ul class="reason-list">
              <li>
                <span class="reason-dot green"></span>
                Strong weather suitability for current conditions
              </li>
              <li>
                <span class="reason-dot yellow"></span>
                Good occasion alignment for the selected context
              </li>
              <li>
                <span class="reason-dot blue"></span>
                Colour combination is visually consistent
              </li>
              <li>
                <span class="reason-dot green"></span>
                Supports sustainable wardrobe rotation
              </li>
              <li>
                <span class="reason-dot green"></span>
                Comfort is likely to be high in the current weather
              </li>
            </ul>
          </div>

          <div class="action-stack">
            <button class="save-btn" type="button" @click="saveOutfit">
              Save Outfit
            </button>
            <button class="secondary-btn" type="button" @click="generateRecommendations">
              Generate Another
            </button>
            <button class="feedback-btn" type="button" @click="goToFeedback">
              Give Feedback
            </button>
          </div>
        </article>
      </div>

      <div class="right-column">
        <article class="side-card">
          <h3>Context Used</h3>

          <div class="context-list">
            <div class="context-row">
              <span>Occasion</span>
              <strong>{{ formatText(occasion) }}</strong>
            </div>

            <div class="context-row">
              <span>Temperature</span>
              <strong>{{ formatTemperature(activeWeather?.temperature) }}</strong>
            </div>

            <div class="context-row">
              <span>Season</span>
              <strong>{{ deriveSeason(activeWeather?.temperature) }}</strong>
            </div>

            <div class="context-row">
              <span>Condition</span>
              <strong>{{ activeWeather?.condition || 'N/A' }}</strong>
            </div>

            <div class="context-row">
              <span>Location</span>
              <strong>{{ activeWeather?.city || location || 'N/A' }}</strong>
            </div>

            <div class="context-row">
              <span>Source</span>
              <strong>
                {{
                  activeWeather?.fallback_used
                    ? 'Last Snapshot'
                    : formatText(activeWeather?.source || 'Live')
                }}
              </strong>
            </div>
          </div>
        </article>

        <article v-if="otherOutfits.length" class="side-card">
          <h3>Other Outfits</h3>

          <div class="other-outfits-list">
            <button
              v-for="(outfit, index) in otherOutfits"
              :key="outfit.rank || index"
              type="button"
              class="other-outfit-btn"
              @click="selectOtherOutfit(index)"
            >
              <strong>Outfit {{ index + 1 }}</strong>
              <span>{{ compactOutfitNames(outfit) }}</span>
            </button>
          </div>
        </article>
      </div>
    </section>

    <section v-if="!isLoading && hasGenerated && !topRecommendation" class="empty-card">
      <p>No outfit could be generated for the selected options.</p>
    </section>
  </div>
</template>

<script>
import {
  fetchWeatherWithFallback,
  getRankedOutfits,
  getImageUrl,
} from '../services/api'

export default {
  name: 'RecommendationsPage',

  data() {
    return {
      occasion: 'casual',
      topK: 1,
      maxOutfits: 20,
      location: 'London',

      isLoading: false,
      hasGenerated: false,
      errorMessage: '',
      statusMessage: '',

      activeWeather: null,
      recommendationResult: null,
      selectedRecommendationIndex: 0,
    }
  },

  computed: {
    recommendations() {
      return Array.isArray(this.recommendationResult?.ranked_outfits)
        ? this.recommendationResult.ranked_outfits
        : []
    },

    topRecommendation() {
      return this.recommendations[this.selectedRecommendationIndex] || null
    },

    otherOutfits() {
      if (!this.recommendations.length) return []
      return this.recommendations.filter((_, index) => index !== this.selectedRecommendationIndex)
    },

    displayedTopItems() {
      return this.normalizeOutfitItems(this.topRecommendation)
    },

    summaryCards() {
      if (!this.recommendationResult) return []

      return [
        {
          label: 'Valid Items',
          value: this.recommendationResult.valid_item_count ?? 0,
        },
        {
          label: 'Rejected Items',
          value: this.recommendationResult.rejected_item_count ?? 0,
        },
        {
          label: 'Returned Outfits',
          value: this.recommendationResult.returned_ranked_outfit_count ?? 0,
        },
      ]
    },
  },

  methods: {
    getImageUrl,

    formatText(value) {
      if (!value) return 'N/A'
      const text = String(value).replace(/_/g, ' ')
      return text.charAt(0).toUpperCase() + text.slice(1)
    },

    formatTemperature(value) {
      return typeof value === 'number' ? `${value}°C` : 'N/A'
    },

    deriveSeason(temp) {
      if (typeof temp !== 'number') return 'N/A'
      if (temp < 10) return 'Winter'
      if (temp < 18) return 'Spring'
      if (temp < 26) return 'Summer'
      return 'Summer'
    },

    normalizeOutfitItems(recommendation) {
      if (!recommendation) return []
      if (Array.isArray(recommendation.items)) return recommendation.items
      if (Array.isArray(recommendation.outfit)) return recommendation.outfit
      return []
    },

    resolveImage(item) {
      return item?.image_url || item?.image || item?.image_path || item?.imagePath || ''
    },

    formatSeasons(item) {
      if (!item) return ''
      const seasons = item.seasons || item.suitable_seasons || []
      if (!Array.isArray(seasons) || !seasons.length) return ''
      return seasons.join(', ')
    },

    compactOutfitNames(recommendation) {
      const items = this.normalizeOutfitItems(recommendation)
      if (!items.length) return 'No items'
      return items.map((item) => item.name || this.formatText(item.category)).join(' • ')
    },

    selectOtherOutfit(otherIndex) {
      const actualIndexes = this.recommendations
        .map((_, index) => index)
        .filter((index) => index !== this.selectedRecommendationIndex)

      this.selectedRecommendationIndex = actualIndexes[otherIndex] ?? 0
    },

    async generateRecommendations() {
      this.isLoading = true
      this.hasGenerated = true
      this.errorMessage = ''
      this.statusMessage = 'Fetching latest weather...'
      this.selectedRecommendationIndex = 0

      try {
        const weather = await fetchWeatherWithFallback(this.location || 'London')
        this.activeWeather = weather

        if (weather?.fallback_used) {
          this.statusMessage = 'Live weather failed. Using last saved weather snapshot.'
        } else {
          this.statusMessage = 'Live weather loaded. Generating outfit recommendations...'
        }

        const result = await getRankedOutfits(this.occasion, this.topK, this.maxOutfits)
        this.recommendationResult = result

        if (result?.weather_used) {
          this.activeWeather = {
            ...result.weather_used,
            fallback_used: weather?.fallback_used || false,
            source: result?.weather_used?.source || weather?.source || 'live',
          }
        }

        if (!this.recommendations.length && result?.message) {
          this.statusMessage = result.message
        } else {
          this.statusMessage = ''
        }
      } catch (error) {
        console.error('Failed to generate recommendations:', error)
        this.errorMessage =
          error?.message || 'Failed to fetch weather and generate recommendations.'
        this.recommendationResult = null
      } finally {
        this.isLoading = false
      }
    },

    goToEvaluation() {
      this.$router.push({
        path: '/evaluation',
        query: {
          occasion: this.occasion,
          topK: String(this.topK),
          maxOutfits: String(this.maxOutfits),
          location: this.location || '',
        },
      })
    },

    saveOutfit() {
      window.alert('Save outfit feature can be connected next.')
    },

    goToFeedback() {
      const selected = this.topRecommendation
      if (!selected) {
        window.alert('Please generate an outfit first.')
        return
      }

      const rank = selected.rank || 1
      this.$router.push({
        path: '/feedback',
        query: {
          occasion: this.occasion,
          rank: String(rank),
        },
      })
    },
  },
}
</script>

<style scoped>
.recommendations-page {
  padding: 18px;
  background: #f4f7fb;
  min-height: 100vh;
}

.hero-card,
.controls-card,
.main-result-card,
.side-card,
.summary-card,
.empty-card {
  background: #ffffff;
  border: 1px solid #e7edf5;
  border-radius: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.hero-card {
  padding: 30px 26px;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #47b157;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 800;
}

.hero-card h1 {
  margin: 0 0 10px;
  font-size: 2.1rem;
  color: #192132;
}

.subtitle {
  margin: 0;
  color: #6d7888;
  line-height: 1.5;
}

.controls-card {
  padding: 20px 16px 14px;
  margin-bottom: 16px;
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.field-group {
  display: flex;
  flex-direction: column;
}

.field-group label {
  margin-bottom: 8px;
  font-weight: 700;
  color: #1d2433;
}

.field-group input,
.field-group select {
  height: 52px;
  border-radius: 16px;
  border: 1px solid #d8e0ea;
  background: #f8fafc;
  padding: 0 14px;
  font-size: 1rem;
  outline: none;
}

.actions-row {
  margin-top: 16px;
}

.generate-btn {
  background: #081a46;
  color: #ffffff;
  border: none;
  border-radius: 18px;
  padding: 16px 22px;
  min-width: 280px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
}

.generate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.status-message {
  margin: 14px 2px 0;
  color: #4b5563;
  font-weight: 600;
}

.error-message {
  margin: 14px 2px 0;
  color: #c62828;
  font-weight: 700;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.summary-card {
  padding: 16px 18px;
}

.summary-card p {
  margin: 0 0 8px;
  color: #6d7888;
}

.summary-card h3 {
  margin: 0;
  font-size: 2rem;
  color: #1a2030;
}

.results-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.9fr) minmax(280px, 1fr);
  gap: 16px;
}

.main-result-card {
  padding: 18px;
}

.main-result-card h2 {
  margin: 0 0 16px;
  color: #1a2030;
}

.outfit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 14px;
}

.outfit-item-card {
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: #ffffff;
  overflow: hidden;
}

.item-image-frame {
  height: 210px;
  background: #eef2f7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-placeholder {
  color: #64748b;
  font-weight: 700;
  font-size: 1rem;
}

.item-details {
  padding: 14px;
}

.item-category {
  margin: 0 0 6px;
  color: #6d7888;
  font-size: 0.92rem;
}

.item-details h4 {
  margin: 0 0 6px;
  color: #1d2433;
  font-size: 1.15rem;
}

.item-meta {
  margin: 0;
  color: #6d7888;
  line-height: 1.4;
}

.reason-box {
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: #ffffff;
  padding: 18px;
  margin-bottom: 14px;
}

.reason-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.reason-header h3 {
  margin: 0;
  color: #1d2433;
}

.scoring-link {
  background: transparent;
  border: none;
  color: #47b157;
  font-weight: 800;
  cursor: pointer;
}

.reason-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.reason-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  color: #253041;
}

.reason-dot {
  width: 11px;
  height: 11px;
  border-radius: 999px;
  flex-shrink: 0;
}

.reason-dot.green {
  background: #47b157;
}

.reason-dot.yellow {
  background: #f0b43c;
}

.reason-dot.blue {
  background: #5a8dee;
}

.action-stack {
  display: grid;
  gap: 10px;
}

.save-btn,
.secondary-btn,
.feedback-btn {
  height: 50px;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
}

.save-btn {
  border: none;
  background: #47b157;
  color: #ffffff;
}

.secondary-btn {
  border: 2px solid #47b157;
  background: #ffffff;
  color: #47b157;
}

.feedback-btn {
  border: 1px solid #d8e0ea;
  background: #f8fafc;
  color: #1a2030;
}

.right-column {
  display: grid;
  gap: 16px;
  align-content: start;
}

.side-card {
  padding: 18px;
}

.side-card h3 {
  margin: 0 0 14px;
  color: #1d2433;
}

.context-list {
  display: grid;
  gap: 6px;
}

.context-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #edf2f7;
}

.context-row:last-child {
  border-bottom: none;
}

.context-row span {
  color: #6d7888;
}

.other-outfits-list {
  display: grid;
  gap: 10px;
}

.other-outfit-btn {
  width: 100%;
  text-align: left;
  border: 1px solid #a8b4c7;
  border-radius: 16px;
  background: #ffffff;
  padding: 12px;
  cursor: pointer;
}

.other-outfit-btn strong {
  display: block;
  margin-bottom: 6px;
  color: #1f2937;
}

.other-outfit-btn span {
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.4;
}

.empty-card {
  padding: 26px;
  text-align: center;
  color: #475569;
}

@media (max-width: 1100px) {
  .controls-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .results-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .recommendations-page {
    padding: 12px;
  }

  .controls-grid,
  .summary-grid,
  .outfit-grid {
    grid-template-columns: 1fr;
  }

  .generate-btn {
    width: 100%;
    min-width: 0;
  }

  .reason-header,
  .context-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>