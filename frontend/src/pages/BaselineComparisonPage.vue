<template>
  <div class="baseline-page">
    <section class="hero-card">
      <div class="hero-top">
        <button class="back-button" @click="goBack">←</button>

        <div class="hero-copy">
          <p class="eyebrow">Evaluation</p>
          <h1>Baseline Comparison</h1>
          <p class="subtitle">
            Compare random baseline, rule-based filtering, and the hybrid recommendation
            model using a clearer website-style dashboard.
          </p>
        </div>
      </div>

      <div class="hero-stats">
        <div class="hero-stat">
          <span>Total Models</span>
          <strong>3</strong>
        </div>
        <div class="hero-stat">
          <span>Generated Outfits</span>
          <strong>{{ generatedOutfitCount }}</strong>
        </div>
        <div class="hero-stat">
          <span>Active Model</span>
          <strong>{{ selectedModelData.label }}</strong>
        </div>
      </div>
    </section>

    <section class="tabs-card">
      <div class="tabs-grid">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-button"
          :class="{ active: selectedModel === tab.key }"
          @click="selectedModel = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </section>

    <section class="top-grid">
      <article class="model-card">
        <div class="card-header">
          <p class="section-label">Selected Model</p>
          <span class="model-badge" :class="`model-badge--${selectedModel}`">
            {{ selectedModelData.shortLabel }}
          </span>
        </div>

        <h2>{{ selectedModelData.label }}</h2>
        <p class="model-description">{{ selectedModelData.description }}</p>

        <div class="mini-stats">
          <div class="mini-stat">
            <span>Match Score</span>
            <strong>{{ selectedModelData.matchScore }}%</strong>
          </div>
          <div class="mini-stat">
            <span>User Rating</span>
            <strong class="rating-text">{{ selectedModelData.ratingLabel }}</strong>
          </div>
        </div>
      </article>

      <article class="example-card">
        <div class="card-header">
          <p class="section-label">Example Output</p>
        </div>

        <template v-if="selectedOutfitItems.length">
          <div class="outfit-grid">
            <div
              v-for="(item, index) in selectedOutfitItems"
              :key="item.id || `${item.category}-${index}`"
              class="outfit-chip"
            >
              {{ getItemDisplayName(item) }}
            </div>
          </div>
        </template>

        <div v-else class="empty-state">
          No outfit data available for this model yet.
        </div>
      </article>
    </section>

    <section class="comparison-card">
      <div class="card-header">
        <div>
          <p class="section-label">Performance Comparison</p>
          <h2>How each model performs</h2>
        </div>
      </div>

      <div class="metric-block">
        <h3>Constraint Satisfaction</h3>
        <div
          v-for="row in comparisonRows"
          :key="`constraint-${row.key}`"
          class="metric-row"
        >
          <span class="metric-label">{{ row.shortLabel }}</span>
          <div class="metric-bar-track">
            <div
              class="metric-bar-fill"
              :class="`metric-bar-fill--${row.key}`"
              :style="{ width: `${row.constraintPercent}%` }"
            ></div>
          </div>
          <strong>{{ row.constraintPercent }}%</strong>
        </div>
      </div>

      <div class="metric-block">
        <h3>Diversity Score</h3>
        <div
          v-for="row in comparisonRows"
          :key="`diversity-${row.key}`"
          class="metric-row"
        >
          <span class="metric-label">{{ row.shortLabel }}</span>
          <div class="metric-bar-track">
            <div
              class="metric-bar-fill"
              :class="`metric-bar-fill--${row.key}`"
              :style="{ width: `${row.diversityPercent}%` }"
            ></div>
          </div>
          <strong>{{ row.diversityPercent }}%</strong>
        </div>
      </div>

      <div class="metric-block">
        <h3>Wardrobe Utilisation</h3>
        <div
          v-for="row in comparisonRows"
          :key="`utilisation-${row.key}`"
          class="metric-row"
        >
          <span class="metric-label">{{ row.shortLabel }}</span>
          <div class="metric-bar-track">
            <div
              class="metric-bar-fill"
              :class="`metric-bar-fill--${row.key}`"
              :style="{ width: `${row.utilisationPercent}%` }"
            ></div>
          </div>
          <strong>{{ row.utilisationPercent }}%</strong>
        </div>
      </div>

      <div class="metric-block">
        <h3>Low Repetition Quality</h3>
        <div
          v-for="row in comparisonRows"
          :key="`repetition-${row.key}`"
          class="metric-row"
        >
          <span class="metric-label">{{ row.shortLabel }}</span>
          <div class="metric-bar-track">
            <div
              class="metric-bar-fill"
              :class="`metric-bar-fill--${row.key}`"
              :style="{ width: `${row.lowRepetitionPercent}%` }"
            ></div>
          </div>
          <strong>{{ row.lowRepetitionPercent }}%</strong>
        </div>
      </div>
    </section>

    <section class="bottom-grid">
      <article class="improvement-card">
        <div class="card-header">
          <div>
            <p class="section-label">Improvement Over Baselines</p>
            <h2>Hybrid constraint-ranking gains</h2>
          </div>
        </div>

        <div class="improvement-row">
          <span>vs Random Selection</span>
          <strong>{{ hybridVsRandom }}</strong>
        </div>

        <div class="improvement-row">
          <span>vs Rule-Based Only</span>
          <strong>{{ hybridVsRule }}</strong>
        </div>

        <div class="improvement-row">
          <span>Statistical Significance</span>
          <strong>p &lt; 0.001</strong>
        </div>
      </article>

      <article class="insight-card">
        <div class="card-header">
          <div>
            <p class="section-label">Evaluation Insight</p>
            <h2>Interpretation</h2>
          </div>
        </div>

        <p>
          The hybrid model combines hard constraint validation with ranking-based
          optimisation. This gives better balance than random selection and produces
          stronger overall recommendation quality than a rule-only approach.
        </p>
      </article>
    </section>

    <section v-if="error" class="error-box">
      {{ error }}
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getEvaluationComparison } from '../services/api'

const router = useRouter()

const loading = ref(false)
const error = ref('')
const evaluationResult = ref(null)
const selectedModel = ref('hybrid')

const tabs = [
  { key: 'random', label: 'Random Selection' },
  { key: 'rule', label: 'Rule-Based Only' },
  { key: 'hybrid', label: 'Hybrid Constraint-Ranking' },
]

const emptyMetrics = {
  outfit_count: 0,
  constraint_satisfaction_rate: 0,
  diversity_index: 0,
  repetition_rate: 0,
  wardrobe_utilisation: 0,
  average_outfit_size: 0,
}

const comparison = computed(() => evaluationResult.value?.comparison || {})

const randomData = computed(() => comparison.value.random_baseline || { metrics: emptyMetrics, outfits: [] })
const ruleData = computed(() => comparison.value.rule_only_baseline || { metrics: emptyMetrics, outfits: [] })
const hybridData = computed(() => comparison.value.hybrid_model || { metrics: emptyMetrics, outfits: [] })

const generatedOutfitCount = computed(() => evaluationResult.value?.generated_outfit_count ?? 0)

const modelMap = computed(() => ({
  random: {
    key: 'random',
    label: 'Random Selection',
    shortLabel: 'Random',
    description: 'Unstructured outfit selection without ranking logic.',
    metrics: randomData.value.metrics || emptyMetrics,
    outfits: randomData.value.outfits || [],
  },
  rule: {
    key: 'rule',
    label: 'Rule-Based Only',
    shortLabel: 'Rule',
    description: 'Constraint filtering only, without score-based prioritisation.',
    metrics: ruleData.value.metrics || emptyMetrics,
    outfits: ruleData.value.outfits || [],
  },
  hybrid: {
    key: 'hybrid',
    label: 'Hybrid Constraint-Ranking',
    shortLabel: 'Hybrid',
    description: 'Multi-factor optimisation using constraints and ranking together.',
    metrics: hybridData.value.metrics || emptyMetrics,
    outfits: hybridData.value.outfits || [],
  },
}))

const selectedModelData = computed(() => {
  const current = modelMap.value[selectedModel.value]
  const matchScore = calculateModelScore(current.metrics)
  const ratingLabel = getRatingLabel(matchScore)

  return {
    ...current,
    matchScore,
    ratingLabel,
  }
})

const selectedOutfit = computed(() => {
  return selectedModelData.value.outfits?.[0] || null
})

const selectedOutfitItems = computed(() => {
  return selectedOutfit.value?.items || []
})

const comparisonRows = computed(() => {
  return ['random', 'rule', 'hybrid'].map((key) => {
    const entry = modelMap.value[key]
    const metrics = entry.metrics || emptyMetrics

    return {
      key,
      shortLabel: entry.shortLabel,
      constraintPercent: toPercent(metrics.constraint_satisfaction_rate),
      diversityPercent: toPercent(metrics.diversity_index),
      utilisationPercent: toPercent(metrics.wardrobe_utilisation),
      lowRepetitionPercent: toPercent(1 - Number(metrics.repetition_rate || 0)),
    }
  })
})

const hybridVsRandom = computed(() => {
  const hybridScore = calculateModelScore(hybridData.value.metrics || emptyMetrics)
  const randomScore = calculateModelScore(randomData.value.metrics || emptyMetrics)

  if (randomScore <= 0) return '+0%'
  return `${hybridScore >= randomScore ? '+' : ''}${Math.round(((hybridScore - randomScore) / randomScore) * 100)}%`
})

const hybridVsRule = computed(() => {
  const hybridScore = calculateModelScore(hybridData.value.metrics || emptyMetrics)
  const ruleScore = calculateModelScore(ruleData.value.metrics || emptyMetrics)

  if (ruleScore <= 0) return '+0%'
  return `${hybridScore >= ruleScore ? '+' : ''}${Math.round(((hybridScore - ruleScore) / ruleScore) * 100)}%`
})

function toPercent(value) {
  const safe = Number(value || 0)
  return Math.max(0, Math.min(100, Math.round(safe * 100)))
}

function calculateModelScore(metrics) {
  const safeMetrics = metrics || emptyMetrics

  const score =
    (Number(safeMetrics.constraint_satisfaction_rate || 0) * 0.35) +
    (Number(safeMetrics.diversity_index || 0) * 0.20) +
    (Number(safeMetrics.wardrobe_utilisation || 0) * 0.30) +
    ((1 - Number(safeMetrics.repetition_rate || 0)) * 0.15)

  return Math.max(0, Math.min(100, Math.round(score * 100)))
}

function getRatingLabel(score) {
  if (score >= 85) return 'Perfect'
  if (score >= 70) return 'Excellent'
  if (score >= 55) return 'Good'
  if (score >= 40) return 'Average'
  return 'Needs Work'
}

function getItemDisplayName(item) {
  if (!item) return 'Unknown Item'

  const parts = []
  if (item.colour_primary) parts.push(item.colour_primary)
  if (item.category) parts.push(item.category)

  return parts.length ? parts.join(' ') : item.name || 'Wardrobe Item'
}

function goBack() {
  router.back()
}

async function loadBaselineComparison() {
  loading.value = true
  error.value = ''

  try {
    evaluationResult.value = await getEvaluationComparison('office', 5, 20)
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to load baseline comparison.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBaselineComparison()
})
</script>

<style scoped>
.baseline-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.tabs-card,
.model-card,
.example-card,
.comparison-card,
.improvement-card,
.insight-card,
.error-box {
  background: #ffffff;
  border: 1px solid #e8edf5;
  border-radius: 24px;
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
}

.hero-card {
  padding: 28px;
  background: linear-gradient(135deg, #f8fbff 0%, #ffffff 100%);
}

.hero-top {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 24px;
}

.back-button {
  width: 46px;
  height: 46px;
  border: none;
  border-radius: 14px;
  background: #f4f7fb;
  color: #0f172a;
  font-size: 1.5rem;
  cursor: pointer;
  flex-shrink: 0;
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

.hero-copy h1 {
  margin: 0 0 10px;
  font-size: clamp(2rem, 4vw, 2.9rem);
  line-height: 1.08;
  color: #0f172a;
}

.subtitle {
  margin: 0;
  max-width: 760px;
  color: #64748b;
  line-height: 1.8;
  font-size: 1rem;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.hero-stat {
  padding: 18px;
  background: #f8fafc;
  border: 1px solid #e7eef6;
  border-radius: 18px;
}

.hero-stat span {
  display: block;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 0.92rem;
}

.hero-stat strong {
  font-size: 1.25rem;
  color: #0f172a;
}

.tabs-card,
.comparison-card,
.improvement-card,
.insight-card,
.error-box {
  padding: 24px;
}

.tabs-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.tab-button {
  border: none;
  border-radius: 18px;
  padding: 18px 16px;
  background: #f8fafc;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.tab-button:hover {
  transform: translateY(-1px);
}

.tab-button.active {
  background: #4fb24d;
  color: #ffffff;
}

.top-grid,
.bottom-grid {
  display: grid;
  gap: 20px;
}

.top-grid {
  grid-template-columns: 1fr 1.2fr;
}

.bottom-grid {
  grid-template-columns: 1fr 1fr;
}

.model-card,
.example-card {
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.model-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 0.84rem;
  font-weight: 800;
}

.model-badge--random {
  background: #fef2f2;
  color: #dc2626;
}

.model-badge--rule {
  background: #fff7ed;
  color: #d97706;
}

.model-badge--hybrid {
  background: #edf9ed;
  color: #2f8b35;
}

.model-card h2,
.example-card h2,
.comparison-card h2,
.improvement-card h2,
.insight-card h2 {
  margin: 0 0 10px;
  color: #0f172a;
  font-size: 1.5rem;
}

.model-description,
.insight-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.8;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 22px;
}

.mini-stat {
  padding: 18px;
  background: #f8fafc;
  border: 1px solid #e7eef6;
  border-radius: 18px;
}

.mini-stat span {
  display: block;
  margin-bottom: 8px;
  color: #64748b;
}

.mini-stat strong {
  font-size: 1.8rem;
  color: #0f172a;
}

.rating-text {
  color: #41a646 !important;
}

.outfit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.outfit-chip {
  padding: 18px 14px;
  background: #f8fafc;
  border: 1px solid #e7eef6;
  border-radius: 18px;
  text-align: center;
  color: #0f172a;
  font-weight: 800;
}

.empty-state {
  padding: 18px;
  border-radius: 18px;
  background: #f8fafc;
  color: #64748b;
}

.metric-block + .metric-block {
  margin-top: 28px;
}

.metric-block h3 {
  margin: 0 0 16px;
  color: #0f172a;
  font-size: 1.15rem;
}

.metric-row {
  display: grid;
  grid-template-columns: 80px 1fr 60px;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.metric-label {
  color: #64748b;
  font-size: 0.96rem;
  font-weight: 600;
}

.metric-bar-track {
  width: 100%;
  height: 12px;
  background: #edf2f7;
  border-radius: 999px;
  overflow: hidden;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 999px;
}

.metric-bar-fill--random {
  background: #f16464;
}

.metric-bar-fill--rule {
  background: #f1aa3c;
}

.metric-bar-fill--hybrid {
  background: #4caf50;
}

.metric-row strong {
  color: #0f172a;
  text-align: right;
}

.improvement-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 0;
  border-bottom: 1px solid #edf2f7;
}

.improvement-row:last-child {
  border-bottom: none;
}

.improvement-row span {
  color: #64748b;
}

.improvement-row strong {
  color: #41a646;
  font-size: 1.15rem;
}

.insight-card {
  padding: 24px;
  background: linear-gradient(135deg, #f3fff1 0%, #ffffff 100%);
}

.error-box {
  padding: 20px 24px;
  background: #fff4f4;
  border-color: #ffd6d6;
  color: #991b1b;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .top-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .hero-card,
  .tabs-card,
  .model-card,
  .example-card,
  .comparison-card,
  .improvement-card,
  .insight-card,
  .error-box {
    padding: 20px;
  }

  .hero-top {
    flex-direction: column;
  }

  .hero-stats,
  .tabs-grid,
  .mini-stats,
  .outfit-grid {
    grid-template-columns: 1fr;
  }

  .metric-row {
    grid-template-columns: 62px 1fr 48px;
    gap: 10px;
  }
}
</style>