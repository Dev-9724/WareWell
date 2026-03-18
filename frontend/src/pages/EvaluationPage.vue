<template>
  <div>
    <h1>Evaluation</h1>
    <p>Compare recommendation models using evaluation metrics.</p>

    <form class="evaluation-form" @submit.prevent="loadEvaluation">
      <label>
        User ID
        <input v-model="userId" type="text" required />
      </label>

      <label>
        Occasion
        <select v-model="occasion">
          <option value="casual">Casual</option>
          <option value="smart-casual">Smart Casual</option>
          <option value="office">Office</option>
          <option value="formal">Formal</option>
          <option value="party">Party</option>
          <option value="gym">Gym</option>
        </select>
      </label>

      <label>
        Top K
        <input v-model.number="topK" type="number" min="1" max="10" />
      </label>

      <button type="submit">Run Evaluation</button>
    </form>

    <div v-if="loading" class="info-box">Running evaluation...</div>

    <div v-if="errorMessage" class="error-box">
      {{ errorMessage }}
    </div>

    <div v-if="result" class="evaluation-result">
      <div class="summary-card">
        <h2>Evaluation Summary</h2>
        <p><strong>City:</strong> {{ result.weather_used.city }}</p>
        <p><strong>Temperature:</strong> {{ result.weather_used.temperature }} °C</p>
        <p><strong>Condition:</strong> {{ result.weather_used.condition }}</p>
        <p><strong>Occasion:</strong> {{ result.occasion_used || 'None' }}</p>
        <p><strong>Target Formality:</strong> {{ result.target_formality_used }}</p>
        <p><strong>Valid Items:</strong> {{ result.valid_item_count }}</p>
        <p><strong>Rejected Items:</strong> {{ result.rejected_item_count }}</p>
        <p><strong>Generated Outfits:</strong> {{ result.generated_outfit_count }}</p>
      </div>

      <div class="models-grid">
        <div class="model-card">
          <h2>Random Baseline</h2>
          <MetricView :metrics="result.comparison.random_baseline.metrics" />
          <ModelOutfits :outfits="result.comparison.random_baseline.outfits" />
        </div>

        <div class="model-card">
          <h2>Rule-Only Baseline</h2>
          <MetricView :metrics="result.comparison.rule_only_baseline.metrics" />
          <ModelOutfits :outfits="result.comparison.rule_only_baseline.outfits" />
        </div>

        <div class="model-card">
          <h2>Hybrid Model</h2>
          <MetricView :metrics="result.comparison.hybrid_model.metrics" />
          <ModelOutfits :outfits="result.comparison.hybrid_model.outfits" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineComponent, h } from 'vue'
import { getEvaluationComparison } from '../services/api'

const userId = ref('dev_mdx_user')
const occasion = ref('office')
const topK = ref(5)

const loading = ref(false)
const errorMessage = ref('')
const result = ref(null)

async function loadEvaluation() {
  loading.value = true
  errorMessage.value = ''
  result.value = null

  try {
    result.value = await getEvaluationComparison(userId.value, occasion.value, topK.value, 20)
  } catch (err) {
    errorMessage.value = 'Failed to run evaluation.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const MetricView = defineComponent({
  props: {
    metrics: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    return () =>
      h('div', { class: 'metrics-box' }, [
        h('p', [h('strong', 'Outfit Count: '), String(props.metrics.outfit_count ?? 0)]),
        h('p', [h('strong', 'Constraint Satisfaction: '), String(props.metrics.constraint_satisfaction_rate ?? 0)]),
        h('p', [h('strong', 'Diversity Index: '), String(props.metrics.diversity_index ?? 0)]),
        h('p', [h('strong', 'Repetition Rate: '), String(props.metrics.repetition_rate ?? 0)]),
        h('p', [h('strong', 'Wardrobe Utilisation: '), String(props.metrics.wardrobe_utilisation ?? 0)]),
        h('p', [h('strong', 'Average Outfit Size: '), String(props.metrics.average_outfit_size ?? 0)]),
      ])
  },
})

const ModelOutfits = defineComponent({
  props: {
    outfits: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    return () =>
      h(
        'div',
        { class: 'outfits-box' },
        props.outfits.map((outfit) =>
          h('div', { class: 'mini-outfit-card', key: outfit.outfit_id }, [
            h('p', [h('strong', `Outfit #${outfit.outfit_id}`)]),
            outfit.score !== undefined ? h('p', [`Score: ${outfit.score}`]) : null,
            h(
              'ul',
              {},
              (outfit.items || []).map((item) =>
                h('li', { key: item.id || `${item.category}-${item.colour_primary}` }, `${item.category} - ${item.colour_primary}`)
              )
            ),
          ])
        )
      )
  },
})
</script>

<style scoped>
.evaluation-form {
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

.summary-card,
.model-card {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 16px;
}

.evaluation-result {
  margin-top: 32px;
  display: grid;
  gap: 24px;
}

.models-grid {
  display: grid;
  gap: 20px;
}

.metrics-box,
.outfits-box {
  margin-top: 12px;
}

.mini-outfit-card {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;
}

.info-box,
.error-box {
  margin-top: 20px;
  padding: 16px;
  border-radius: 8px;
  max-width: 520px;
}

.info-box {
  background: #e0f2fe;
  color: #075985;
}

.error-box {
  background: #fee2e2;
  color: #991b1b;
}
</style>