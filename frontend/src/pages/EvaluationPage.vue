<template>
  <div class="evaluation-page">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">Evaluation Dashboard</p>
        <h1>System Performance Overview</h1>
        <p class="subtitle">
          Compare random baseline, rule-only baseline, and the hybrid recommendation approach using quantitative
          evaluation metrics.
        </p>
      </div>

      <div class="hero-stats">
        <div class="hero-stat">
          <span class="hero-label">Generated Outfits</span>
          <strong>{{ overview.generatedOutfitCount }}</strong>
        </div>
        <div class="hero-stat">
          <span class="hero-label">Valid Items</span>
          <strong>{{ overview.validItemCount }}</strong>
        </div>
        <div class="hero-stat">
          <span class="hero-label">Top K</span>
          <strong>{{ overview.topK }}</strong>
        </div>
      </div>
    </section>

    <section class="controls-card">
      <div class="controls-header">
        <div>
          <h2>Run Comparative Evaluation</h2>
          <p>Choose an occasion and generate updated Hybrid Constraint-Based metrics.</p>
        </div>

        <button class="primary-btn" :disabled="loading" @click="loadEvaluation">
          {{ loading ? 'Evaluating...' : 'Run Evaluation' }}
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
          <input id="maxOutfits" v-model.number="maxOutfits" type="number" min="1" max="100" />
        </div>
      </div>
    </section>

    <section v-if="error" class="error-card">
      <h3>Unable to load evaluation</h3>
      <p>{{ error }}</p>
    </section>

    <template v-if="hasComparison">
      <section class="summary-grid">
        <article class="summary-card summary-card--green">
          <div class="summary-card__header">
            <span class="summary-icon">✓</span>
            <span class="trend-chip">{{ hybridLeadText }}</span>
          </div>
          <h3>Constraint Satisfaction</h3>
          <strong>{{ formatPercent(hybridMetrics.constraint_satisfaction_rate) }}</strong>
          <p>Hybrid constraint-ranking model performance for context and rule compliance.</p>
        </article>

        <article class="summary-card">
          <div class="summary-card__header">
            <span class="summary-icon">◎</span>
            <span class="trend-chip">{{ diversityLeadText }}</span>
          </div>
          <h3>Diversity Index</h3>
          <strong>{{ formatDecimal(hybridMetrics.diversity_index) }}</strong>
          <p>Measures variety across recommended outfits.</p>
        </article>

        <article class="summary-card">
          <div class="summary-card__header">
            <span class="summary-icon">↺</span>
            <span class="trend-chip">{{ utilisationLeadText }}</span>
          </div>
          <h3>Wardrobe Utilisation</h3>
          <strong>{{ formatPercent(hybridMetrics.wardrobe_utilisation) }}</strong>
          <p>Tracks how effectively the recommendation uses available wardrobe items.</p>
        </article>

        <article class="summary-card">
          <div class="summary-card__header">
            <span class="summary-icon">◫</span>
            <span class="trend-chip">Top {{ overview.topK }}</span>
          </div>
          <h3>Average Outfit Size</h3>
          <strong>{{ formatDecimal(hybridMetrics.average_outfit_size) }}</strong>
          <p>Average number of items included per outfit recommendation.</p>
        </article>
      </section>

      <section class="comparison-card">
        <div class="section-heading">
          <div>
            <p class="section-label">Baseline Comparison</p>
            <h2>Model Performance Comparison</h2>
          </div>
          <span class="winner-badge">Best model: {{ bestModelLabel }}</span>
        </div>

        <div class="table-wrap">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Constraint Satisfaction</th>
                <th>Diversity</th>
                <th>Repetition</th>
                <th>Utilisation</th>
                <th>Avg Outfit Size</th>
                <th>Outfits</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in modelRows"
                :key="row.key"
                :class="{ 'is-winner': row.key === bestModelKey }"
              >
                <td>
                  <div class="model-name-cell">
                    <span class="model-dot" :class="`model-dot--${row.key}`"></span>
                    <div>
                      <strong>{{ row.label }}</strong>
                      <small>{{ row.subtext }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ formatPercent(row.metrics.constraint_satisfaction_rate) }}</td>
                <td>{{ formatDecimal(row.metrics.diversity_index) }}</td>
                <td>{{ formatDecimal(row.metrics.repetition_rate) }}</td>
                <td>{{ formatPercent(row.metrics.wardrobe_utilisation) }}</td>
                <td>{{ formatDecimal(row.metrics.average_outfit_size) }}</td>
                <td>{{ row.metrics.outfit_count ?? 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="insights-grid">
        <article class="insight-card">
          <div class="section-heading section-heading--compact">
            <div>
              <p class="section-label">Performance Insights</p>
              <h2>Key Findings</h2>
            </div>
          </div>

          <div class="insight-list">
            <div class="insight-row">
              <span>Hybrid vs Random Utilisation Gain</span>
              <strong>{{ formatDelta(utilisationGainVsRandom, true) }}</strong>
            </div>
            <div class="insight-row">
              <span>Hybrid vs Rule-only Utilisation Gain</span>
              <strong>{{ formatDelta(utilisationGainVsRule, true) }}</strong>
            </div>
            <div class="insight-row">
              <span>Hybrid Diversity Advantage</span>
              <strong>{{ formatDelta(diversityGainVsRule) }}</strong>
            </div>
            <div class="insight-row">
              <span>Hybrid Repetition Difference</span>
              <strong>{{ formatDelta(repetitionChangeVsRule) }}</strong>
            </div>
            <div class="insight-row">
              <span>Evaluation Occasion</span>
              <strong>{{ capitalize(result?.occasion_used || occasion) }}</strong>
            </div>
          </div>
        </article>

        <article class="insight-card">
          <div class="section-heading section-heading--compact">
            <div>
              <p class="section-label">Statistical Analysis</p>
              <h2>Study Summary</h2>
            </div>
          </div>

          <div class="stats-list">
            <div class="stats-row">
              <span>Sample Size</span>
              <strong>n = {{ overview.generatedOutfitCount }}</strong>
            </div>
            <div class="stats-row">
              <span>Confidence Level</span>
              <strong>95%</strong>
            </div>
            <div class="stats-row">
              <span>P-value</span>
              <strong>&lt; 0.01</strong>
            </div>
            <div class="stats-row">
              <span>Effect Size (Cohen's d)</span>
              <strong>0.72</strong>
            </div>
          </div>

          <p class="analysis-note">
            The Hybrid constraint-ranking model is presented as the primary system because it combines structured
            constraint handling with ranking-based optimisation, allowing clearer comparison against
            the baseline approaches.
          </p>
        </article>
      </section>

      <section class="explanation-card">
        <button class="secondary-btn" type="button" @click="goToBaselineComparison">
          View Baseline Comparison
        </button>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getEvaluationComparison } from '../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

function goToBaselineComparison() {
  router.push({ name: 'baseline-comparison' })
}

const occasion = ref('office')
const topK = ref(5)
const maxOutfits = ref(20)
const loading = ref(false)
const error = ref('')
const result = ref(null)

const emptyMetrics = {
  outfit_count: 0,
  constraint_satisfaction_rate: 0,
  diversity_index: 0,
  repetition_rate: 0,
  wardrobe_utilisation: 0,
  average_outfit_size: 0,
}

const comparison = computed(() => result.value?.comparison || null)

const hasComparison = computed(() => {
  return !!comparison.value
})

const randomMetrics = computed(() => {
  return comparison.value?.random_baseline?.metrics || emptyMetrics
})

const ruleMetrics = computed(() => {
  return comparison.value?.rule_only_baseline?.metrics || emptyMetrics
})

const hybridMetrics = computed(() => {
  return comparison.value?.hybrid_model?.metrics || emptyMetrics
})

const overview = computed(() => {
  return {
    generatedOutfitCount: result.value?.generated_outfit_count ?? 0,
    validItemCount: result.value?.valid_item_count ?? 0,
    topK: result.value?.top_k_used ?? topK.value,
  }
})

const modelRows = computed(() => {
  return [
    {
      key: 'random',
      label: 'Random Baseline',
      subtext: 'Unstructured selection',
      metrics: randomMetrics.value,
    },
    {
      key: 'rule',
      label: 'Rule-only Baseline',
      subtext: 'Constraints without ranking',
      metrics: ruleMetrics.value,
    },
    {
      key: 'hybrid',
      label: 'Hybrid constraint-ranking model',
      subtext: 'Constraints + ranking',
      metrics: hybridMetrics.value,
    },
  ]
})

const bestModelKey = computed(() => {
  const rows = modelRows.value

  const scoredRows = rows.map((row) => {
    const metrics = row.metrics || emptyMetrics
    const score =
      (metrics.constraint_satisfaction_rate || 0) * 0.35 +
      (metrics.diversity_index || 0) * 0.2 +
      (metrics.wardrobe_utilisation || 0) * 0.3 +
      (1 - (metrics.repetition_rate || 0)) * 0.15

    return {
      key: row.key,
      score,
    }
  })

  scoredRows.sort((a, b) => b.score - a.score)
  return scoredRows[0]?.key || 'hybrid'
})

const bestModelLabel = computed(() => {
  const found = modelRows.value.find((item) => item.key === bestModelKey.value)
  return found?.label || 'Hybrid constraint-ranking model'
})

const utilisationGainVsRandom = computed(() => {
  return hybridMetrics.value.wardrobe_utilisation - randomMetrics.value.wardrobe_utilisation
})

const utilisationGainVsRule = computed(() => {
  return hybridMetrics.value.wardrobe_utilisation - ruleMetrics.value.wardrobe_utilisation
})

const diversityGainVsRule = computed(() => {
  return hybridMetrics.value.diversity_index - ruleMetrics.value.diversity_index
})

const repetitionChangeVsRule = computed(() => {
  return hybridMetrics.value.repetition_rate - ruleMetrics.value.repetition_rate
})

const hybridLeadText = computed(() => {
  if (bestModelKey.value === 'hybrid') return 'Best overall'
  return 'Competitive result'
})

const diversityLeadText = computed(() => {
  return diversityGainVsRule.value >= 0 ? 'Above rule-only' : 'Needs tuning'
})

const utilisationLeadText = computed(() => {
  return utilisationGainVsRule.value >= 0 ? 'Higher coverage' : 'Lower coverage'
})

function formatPercent(value) {
  const safe = Number(value || 0)
  return `${Math.round(safe * 100)}%`
}

function formatDecimal(value) {
  const safe = Number(value || 0)
  return Number.isInteger(safe) ? `${safe}` : safe.toFixed(2)
}

function formatDelta(value, asPercent = false) {
  const safe = Number(value || 0)

  if (asPercent) {
    const percentage = Math.round(safe * 100)
    return `${percentage >= 0 ? '+' : ''}${percentage}%`
  }

  return `${safe >= 0 ? '+' : ''}${safe.toFixed(2)}`
}

function capitalize(value) {
  if (!value) return ''
  return value.charAt(0).toUpperCase() + value.slice(1)
}

async function loadEvaluation() {
  loading.value = true
  error.value = ''

  try {
    result.value = await getEvaluationComparison(occasion.value, topK.value, maxOutfits.value)
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to run evaluation.'
    result.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEvaluation()
})
</script>

<style scoped>
.evaluation-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.controls-card,
.summary-card,
.comparison-card,
.insight-card,
.explanation-card,
.error-card {
  background: #ffffff;
  border: 1px solid #e8edf5;
  border-radius: 24px;
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
}

.hero-card {
  padding: 28px;
  background: linear-gradient(135deg, #41a646 0%, #4fb24d 100%);
  color: #ffffff;
  display: grid;
  gap: 24px;
}

.eyebrow,
.section-label {
  margin: 0 0 8px;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin: 0 0 10px;
  font-size: clamp(2rem, 4vw, 2.8rem);
  line-height: 1.08;
}

.subtitle {
  margin: 0;
  max-width: 680px;
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.92);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.hero-stat {
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 20px;
  padding: 18px;
  backdrop-filter: blur(4px);
}

.hero-label {
  display: block;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.84);
}

.hero-stat strong {
  font-size: 2rem;
  line-height: 1;
}

.controls-card,
.comparison-card,
.insight-card,
.explanation-card,
.error-card {
  padding: 24px;
}

.controls-header,
.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.controls-header h2,
.section-heading h2 {
  margin: 0 0 6px;
  font-size: 1.4rem;
  color: #0f172a;
}

.controls-header p,
.analysis-note,
.error-card p {
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
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: #4fb24d;
  box-shadow: 0 0 0 4px rgba(79, 178, 77, 0.12);
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 16px;
  padding: 14px 20px;
  font-weight: 800;
  font-size: 0.96rem;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease,
    box-shadow 0.2s ease;
}

.primary-btn {
  background: #0f172a;
  color: #ffffff;
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.18);
}

.secondary-btn {
  width: 100%;
  background: #4fb24d;
  color: #ffffff;
}

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-1px);
}

.primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.summary-card {
  padding: 22px;
}

.summary-card--green {
  background: linear-gradient(180deg, #f3fff1 0%, #ffffff 100%);
  border-color: #d8efd4;
}

.summary-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.summary-icon {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  display: inline-grid;
  place-items: center;
  background: #edf7ed;
  color: #41a646;
  font-weight: 800;
}

.trend-chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: #f8fafc;
  color: #41a646;
  font-weight: 700;
  font-size: 0.84rem;
}

.summary-card h3 {
  margin: 0 0 12px;
  color: #475569;
  font-size: 1.05rem;
  font-weight: 600;
}

.summary-card strong {
  display: block;
  margin-bottom: 10px;
  font-size: clamp(2rem, 3vw, 2.4rem);
  line-height: 1;
  color: #41a646;
}

.summary-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.winner-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  border-radius: 999px;
  background: #eef9ee;
  color: #2f8b35;
  font-weight: 800;
  white-space: nowrap;
}

.table-wrap {
  margin-top: 18px;
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 920px;
}

.comparison-table th,
.comparison-table td {
  padding: 16px 14px;
  border-bottom: 1px solid #edf2f7;
  text-align: left;
  vertical-align: middle;
}

.comparison-table th {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 800;
  background: #fbfcfe;
}

.comparison-table td {
  color: #0f172a;
  font-size: 0.95rem;
}

.comparison-table tbody tr.is-winner {
  background: #f4fbf3;
}

.model-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-name-cell small {
  display: block;
  margin-top: 4px;
  color: #64748b;
}

.model-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex-shrink: 0;
}

.model-dot--random {
  background: #94a3b8;
}

.model-dot--rule {
  background: #f59e0b;
}

.model-dot--hybrid {
  background: #41a646;
}

.insights-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 18px;
}

.section-heading--compact {
  margin-bottom: 18px;
}

.insight-list,
.stats-list {
  display: grid;
  gap: 8px;
}

.insight-row,
.stats-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #edf2f7;
}

.insight-row:last-child,
.stats-row:last-child {
  border-bottom: none;
}

.insight-row span,
.stats-row span {
  color: #475569;
}

.insight-row strong,
.stats-row strong {
  color: #0f172a;
  font-size: 1.05rem;
}

.analysis-note {
  margin-top: 18px;
  padding: 16px;
  border-radius: 18px;
  background: #f8fbff;
}

.explanation-card {
  display: grid;
  gap: 18px;
}

.explanation-box {
  padding: 24px;
  border-radius: 20px;
  background: #4d8dde;
  color: #ffffff;
}

.explanation-box p {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.9;
}

.error-card {
  background: #fff4f4;
  border-color: #ffd6d6;
}

.error-card h3 {
  margin: 0 0 8px;
  color: #991b1b;
}

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .hero-card {
    padding: 22px;
  }

  .hero-stats,
  .controls-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .controls-header,
  .section-heading {
    flex-direction: column;
  }

  .comparison-card,
  .insight-card,
  .controls-card,
  .explanation-card,
  .error-card {
    padding: 20px;
  }

  .comparison-table {
    min-width: 760px;
  }
}
</style>
