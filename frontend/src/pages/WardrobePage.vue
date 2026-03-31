<template>
  <div class="wardrobe-page">
    <section class="page-hero">
      <div class="hero-text">
        <p class="eyebrow">Closet Overview</p>
        <h1>Wardrobe Collection</h1>
        <p class="subtitle">
          Browse clothing items by category, monitor usage, and review outfit-ready inventory.
        </p>
      </div>

      <router-link class="primary-btn" to="/add-item">
        + Add New Item
      </router-link>
    </section>

    <section class="stats-grid">
      <div class="stat-card">
        <span>Total Items</span>
        <strong>{{ filteredItems.length }}</strong>
      </div>
      <div class="stat-card">
        <span>Most Worn</span>
        <strong>{{ mostWornLabel }}</strong>
      </div>
      <div class="stat-card">
        <span>Average Cost</span>
        <strong>£{{ averageCost }}</strong>
      </div>
      <div class="stat-card">
        <span>Rain Ready Items</span>
        <strong>{{ rainReadyCount }}</strong>
      </div>
    </section>

    <section class="toolbar-card">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          :class="['tab-btn', { active: activeCategory === tab.value }]"
          @click="activeCategory = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="search-box">
        <input
          v-model="searchText"
          type="text"
          placeholder="Search by item name, category or colour"
        />
      </div>
    </section>

    <section v-if="loading" class="info-card">
      Loading wardrobe items...
    </section>

    <section v-else-if="error" class="error-card">
      {{ error }}
    </section>

    <section v-else-if="filteredItems.length === 0" class="info-card">
      No wardrobe items found for your account.
    </section>

    <section v-else class="wardrobe-grid">
      <article
        v-for="item in filteredItems"
        :key="item.id"
        class="item-card"
      >
        <div class="item-image-wrap">
          <img
            v-if="item.image_url"
            :src="getImageUrl(item.image_url)"
            :alt="item.name || item.category"
            class="item-image"
          />
          <div v-else class="item-image-placeholder">
            {{ item.category }}
          </div>
        </div>

        <div class="item-body">
          <div class="item-header">
            <div>
              <h3>{{ item.name || item.category }}</h3>
              <p class="item-meta">{{ item.category }}</p>
            </div>

            <button class="delete-btn" @click="handleDelete(item.id)">
              Delete
            </button>
          </div>

          <div class="item-details">
            <span class="detail-chip">{{ item.colour_primary || 'No colour' }}</span>
            <span class="detail-chip">{{ formatSeason(item.season) }}</span>
            <span class="detail-chip">
              {{ item.rain_suitable ? 'Rain Ready' : 'Not Rain Ready' }}
            </span>
            <span v-if="item.occasion" class="detail-chip">{{ item.occasion }}</span>
          </div>

          <div class="item-stats">
            <div>
              <span>Wear Count</span>
              <strong>{{ item.wear_count ?? 0 }}</strong>
            </div>
            <div>
              <span>Cost</span>
              <strong>£{{ Number(item.cost || 0).toFixed(2) }}</strong>
            </div>
            <div>
              <span>Formality</span>
              <strong>{{ item.formality_level ?? 0 }}/10</strong>
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { deleteWardrobeItem, getImageUrl, getWardrobeItems } from '../services/api'

const items = ref([])
const loading = ref(false)
const error = ref('')
const searchText = ref('')
const activeCategory = ref('all')

const tabs = [
  { label: 'All', value: 'all' },
  { label: 'Tops', value: 'Top' },
  { label: 'Bottoms', value: 'Bottom' },
  { label: 'Shoes', value: 'Shoes' },
  { label: 'Outerwear', value: 'Outerwear' },
  { label: 'Accessories', value: 'Accessory' },
]

const filteredItems = computed(() => {
  let output = [...items.value]

  if (activeCategory.value !== 'all') {
    output = output.filter((item) => item.category === activeCategory.value)
  }

  const query = searchText.value.trim().toLowerCase()
  if (query) {
    output = output.filter((item) => {
      return (
        String(item.name || '').toLowerCase().includes(query) ||
        String(item.category || '').toLowerCase().includes(query) ||
        String(item.colour_primary || '').toLowerCase().includes(query)
      )
    })
  }

  return output
})

const mostWornLabel = computed(() => {
  if (!items.value.length) return '—'

  const sorted = [...items.value].sort((a, b) => (b.wear_count || 0) - (a.wear_count || 0))
  const best = sorted[0]
  return best?.name || best?.category || '—'
})

const averageCost = computed(() => {
  if (!items.value.length) return '0.00'
  const total = items.value.reduce((sum, item) => sum + Number(item.cost || 0), 0)
  return (total / items.value.length).toFixed(2)
})

const rainReadyCount = computed(() => {
  return items.value.filter((item) => item.rain_suitable).length
})

function formatSeason(season) {
  if (!Array.isArray(season) || season.length === 0) return 'All Seasons'
  return season.join(', ')
}

async function loadItems() {
  loading.value = true
  error.value = ''

  try {
    items.value = await getWardrobeItems()
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to load wardrobe items.'
  } finally {
    loading.value = false
  }
}

async function handleDelete(itemId) {
  const confirmed = window.confirm('Are you sure you want to delete this item?')
  if (!confirmed) return

  try {
    await deleteWardrobeItem(itemId)
    items.value = items.value.filter((item) => item.id !== itemId)
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Failed to delete wardrobe item.'
  }
}

onMounted(loadItems)
</script>

<style scoped>
.wardrobe-page {
  display: grid;
  gap: 24px;
}

.page-hero,
.toolbar-card,
.stat-card,
.item-card,
.info-card,
.error-card {
  background: white;
  border: 1px solid #e3e8f2;
  border-radius: 20px;
  box-shadow: 0 12px 30px rgba(8, 18, 37, 0.04);
}

.page-hero,
.toolbar-card,
.info-card,
.error-card {
  padding: 24px;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 8px;
  color: #1dd1a1;
  font-weight: 800;
  text-transform: uppercase;
}

.page-hero h1 {
  margin: 0 0 8px;
  color: #081225;
}

.subtitle {
  margin: 0;
  color: #6a7790;
  line-height: 1.6;
}

.primary-btn {
  text-decoration: none;
  background: #081225;
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  padding: 18px;
  display: grid;
  gap: 8px;
}

.stat-card span {
  color: #6a7790;
  font-size: 0.9rem;
}

.stat-card strong {
  color: #081225;
  font-size: 1.5rem;
}

.toolbar-card {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tab-btn {
  border: 1px solid #d7e0ec;
  background: #f8fbff;
  color: #31507f;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 700;
}

.tab-btn.active {
  background: #081225;
  color: white;
  border-color: #081225;
}

.search-box input {
  width: 320px;
  max-width: 100%;
  padding: 12px 14px;
  border: 1px solid #d7e0ec;
  border-radius: 12px;
}

.info-card {
  color: #31507f;
}

.error-card {
  background: #fff1f1;
  color: #9b1c1c;
}

.wardrobe-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.item-card {
  overflow: hidden;
}

.item-image-wrap {
  height: 240px;
  background: #f5f7fb;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-image-placeholder {
  height: 100%;
  display: grid;
  place-items: center;
  color: #6a7790;
  font-weight: 700;
}

.item-body {
  padding: 18px;
  display: grid;
  gap: 16px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.item-header h3 {
  margin: 0 0 6px;
  color: #081225;
}

.item-meta {
  margin: 0;
  color: #6a7790;
}

.delete-btn {
  border: none;
  background: #fee2e2;
  color: #b91c1c;
  padding: 10px 12px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.item-details {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.detail-chip {
  background: #eef5ff;
  color: #31507f;
  padding: 8px 12px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.9rem;
}

.item-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.item-stats div {
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 12px;
  display: grid;
  gap: 6px;
}

.item-stats span {
  color: #6a7790;
  font-size: 0.85rem;
}

.item-stats strong {
  color: #081225;
}

@media (max-width: 960px) {
  .stats-grid,
  .wardrobe-grid {
    grid-template-columns: 1fr;
  }

  .toolbar-card,
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-stats {
    grid-template-columns: 1fr;
  }
}
</style>