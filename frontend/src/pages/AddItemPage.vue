<template>
  <div>
    <h1>Add Item</h1>
    <p>Add a new wardrobe item to the backend database.</p>

    <form class="item-form" @submit.prevent="submitItem">
      <label>
        User ID
        <input v-model="form.user_id" type="text" required />
      </label>

      <label>
        Category
        <select v-model="form.category" required>
          <option value="">Select category</option>
          <option value="top">Top</option>
          <option value="bottom">Bottom</option>
          <option value="shoes">Shoes</option>
          <option value="outerwear">Outerwear</option>
          <option value="accessory">Accessory</option>
        </select>
      </label>

      <label>
        Primary Colour
        <input v-model="form.colour_primary" type="text" required />
      </label>

      <label>
        Secondary Colour
        <input v-model="form.colour_secondary" type="text" />
      </label>

      <label>
        Formality Level
        <input v-model.number="form.formality_level" type="number" min="1" max="10" required />
      </label>

      <label>
        Season (comma separated)
        <input v-model="seasonInput" type="text" placeholder="spring, autumn" required />
      </label>

      <label>
        Temperature Min
        <input v-model.number="form.temperature_min" type="number" required />
      </label>

      <label>
        Temperature Max
        <input v-model.number="form.temperature_max" type="number" required />
      </label>

      <label>
        Rain Suitable
        <select v-model="form.rain_suitable" required>
          <option :value="true">Yes</option>
          <option :value="false">No</option>
        </select>
      </label>

      <label>
        Wear Count
        <input v-model.number="form.wear_count" type="number" min="0" required />
      </label>

      <label>
        Cost
        <input v-model.number="form.cost" type="number" min="0" step="0.01" required />
      </label>

      <label>
        Image URL
        <input v-model="form.image_url" type="text" />
      </label>

      <button type="submit">Add Item</button>
    </form>

    <div v-if="successMessage" class="success-box">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="error-box">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { addWardrobeItem } from '../services/api'

const form = ref({
  user_id: 'dev_mdx_user',
  category: '',
  colour_primary: '',
  colour_secondary: '',
  formality_level: 5,
  temperature_min: 5,
  temperature_max: 20,
  rain_suitable: true,
  wear_count: 0,
  cost: 0,
  image_url: '',
})

const seasonInput = ref('spring, autumn')
const successMessage = ref('')
const errorMessage = ref('')

async function submitItem() {
  successMessage.value = ''
  errorMessage.value = ''

  const payload = {
    ...form.value,
    season: seasonInput.value
      .split(',')
      .map((s) => s.trim())
      .filter((s) => s.length > 0),
    last_worn_date: null,
  }

  try {
    await addWardrobeItem(payload)

    successMessage.value = 'Wardrobe item added successfully.'

    form.value = {
      user_id: 'dev_mdx_user',
      category: '',
      colour_primary: '',
      colour_secondary: '',
      formality_level: 5,
      temperature_min: 5,
      temperature_max: 20,
      rain_suitable: true,
      wear_count: 0,
      cost: 0,
      image_url: '',
    }

    seasonInput.value = 'spring, autumn'
  } catch (err) {
    errorMessage.value = 'Failed to add wardrobe item.'
    console.error(err)
  }
}
</script>

<style scoped>
.item-form {
  margin-top: 24px;
  display: grid;
  gap: 16px;
  max-width: 500px;
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

.success-box {
  margin-top: 20px;
  padding: 16px;
  background: #dcfce7;
  color: #166534;
  border-radius: 8px;
  max-width: 500px;
}

.error-box {
  margin-top: 20px;
  padding: 16px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  max-width: 500px;
}
</style>