<template>
  <div class="add-item-page">
    <div class="page-card">
      <div class="page-header">
        <p class="eyebrow">Wardrobe</p>
        <h1>Add New Item</h1>
        <p class="subtitle">
          Add clothing items quickly with only the most important details.
        </p>
      </div>

      <form class="item-form" @submit.prevent="handleSubmit">
        <div class="form-grid">
          <div class="form-group full-width">
            <label for="name">Item Name</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              placeholder="e.g. Red Hoodie"
              required
            />
          </div>

          <div class="form-group">
            <label for="category">Category</label>
            <select id="category" v-model="form.category" required>
              <option disabled value="">Select category</option>
              <option value="Top">Top</option>
              <option value="Bottom">Bottom</option>
              <option value="Shoes">Shoes</option>
              <option value="Outerwear">Outerwear</option>
              <option value="Accessory">Accessory</option>
            </select>
          </div>

          <div class="form-group">
            <label for="primaryColour">Primary Colour</label>
            <input
              id="primaryColour"
              v-model="form.colour_primary"
              type="text"
              placeholder="e.g. Red"
              required
            />
          </div>

          <div class="form-group">
            <label for="cost">Cost (£)</label>
            <input
              id="cost"
              v-model="form.cost"
              type="number"
              min="0"
              step="0.01"
              placeholder="e.g. 25.99"
              required
            />
          </div>

          <div class="form-group">
            <label for="occasion">Occasion</label>
            <select id="occasion" v-model="form.occasion" required>
              <option disabled value="">Select occasion</option>
              <option value="Casual">Casual</option>
              <option value="Smart Casual">Smart Casual</option>
              <option value="Formal">Formal</option>
              <option value="Party">Party</option>
              <option value="Sport">Sport</option>
              <option value="Travel">Travel</option>
              <option value="Office">Office</option>
            </select>
          </div>

          <div class="form-group full-width">
            <label>Season</label>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" value="Spring" v-model="form.season" />
                <span>Spring</span>
              </label>

              <label class="checkbox-item">
                <input type="checkbox" value="Summer" v-model="form.season" />
                <span>Summer</span>
              </label>

              <label class="checkbox-item">
                <input type="checkbox" value="Autumn" v-model="form.season" />
                <span>Autumn</span>
              </label>

              <label class="checkbox-item">
                <input type="checkbox" value="Winter" v-model="form.season" />
                <span>Winter</span>
              </label>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="checkbox-inline">
              <input type="checkbox" v-model="form.rain_suitable" />
              <span>Rain Suitable</span>
            </label>
          </div>

          <div class="form-group full-width">
            <label for="image">Item Image</label>
            <input
              id="image"
              type="file"
              accept="image/*"
              @change="handleImageChange"
            />
          </div>

          <div v-if="previewUrl" class="form-group full-width">
            <label>Image Preview</label>
            <div class="image-preview">
              <img :src="previewUrl" alt="Item preview" />
            </div>
          </div>
        </div>

        <div v-if="errorMessage" class="message error-message">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="message success-message">
          {{ successMessage }}
        </div>

        <button class="save-btn" type="submit" :disabled="isSaving">
          {{ isSaving ? 'Saving...' : 'Save Item' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { addWardrobeItem } from '@/services/api'
import { useAuth } from '@/composables/useAuth'

export default {
  name: 'AddItemPage',
  data() {
    return {
      form: {
        name: '',
        category: '',
        colour_primary: '',
        season: [],
        occasion: '',
        rain_suitable: false,
        cost: '',
      },
      imageFile: null,
      previewUrl: '',
      isSaving: false,
      errorMessage: '',
      successMessage: '',
    }
  },
  methods: {
    handleImageChange(event) {
      const file = event.target.files[0]

      if (!file) {
        this.imageFile = null
        this.previewUrl = ''
        return
      }

      this.imageFile = file
      this.previewUrl = URL.createObjectURL(file)
    },

    resetForm() {
      this.form = {
        name: '',
        category: '',
        colour_primary: '',
        season: [],
        occasion: '',
        rain_suitable: false,
        cost: '',
      }

      this.imageFile = null
      this.previewUrl = ''

      const imageInput = document.getElementById('image')
      if (imageInput) {
        imageInput.value = ''
      }
    },

    async handleSubmit() {
      this.errorMessage = ''
      this.successMessage = ''

      const { getUserId } = useAuth()
      const userId = getUserId()

      if (!userId) {
        this.errorMessage = 'No logged-in user found. Please log in again.'
        return
      }

      if (!this.form.name.trim()) {
        this.errorMessage = 'Please enter an item name.'
        return
      }

      if (!this.form.category) {
        this.errorMessage = 'Please select a category.'
        return
      }

      if (!this.form.colour_primary.trim()) {
        this.errorMessage = 'Please enter a primary colour.'
        return
      }

      if (this.form.season.length === 0) {
        this.errorMessage = 'Please select at least one season.'
        return
      }

      if (!this.form.occasion) {
        this.errorMessage = 'Please select an occasion.'
        return
      }

      if (this.form.cost === '' || Number(this.form.cost) < 0) {
        this.errorMessage = 'Please enter a valid cost.'
        return
      }

      this.isSaving = true

      try {
        const payload = new FormData()
        payload.append('user_id', userId)
        payload.append('name', this.form.name.trim())
        payload.append('category', this.form.category)
        payload.append('colour_primary', this.form.colour_primary.trim())
        payload.append('occasion', this.form.occasion)
        payload.append('rain_suitable', String(this.form.rain_suitable))
        payload.append('cost', String(this.form.cost))

        this.form.season.forEach((item) => {
          payload.append('season', item)
        })

        payload.append('formality_level', this.getFormalityLevel(this.form.occasion))
        payload.append('temperature_min', '0')
        payload.append('temperature_max', '40')
        payload.append('wear_count', '0')

        if (this.imageFile) {
          payload.append('image_file', this.imageFile)
        }

        await addWardrobeItem(payload)

        this.successMessage = 'Item added successfully.'
        this.resetForm()
      } catch (error) {
        this.errorMessage =
          error?.message || 'Something went wrong while saving the item.'
      } finally {
        this.isSaving = false
      }
    },

    getFormalityLevel(occasion) {
      const map = {
        Casual: '2',
        Sport: '2',
        Travel: '3',
        'Smart Casual': '5',
        Office: '6',
        Formal: '8',
        Party: '6',
      }

      return map[occasion] || '5'
    },
  },
}
</script>

<style scoped>
.add-item-page {
  min-height: 100vh;
  padding: 32px 20px;
  background: #f5f7fb;
}

.page-card {
  max-width: 1000px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.page-header {
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 700;
  color: #4f46e5;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.page-header h1 {
  margin: 0 0 10px;
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
}

.subtitle {
  margin: 0;
  font-size: 16px;
  color: #475569;
  line-height: 1.6;
}

.item-form {
  width: 100%;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1e3a8a;
}

.form-group input[type='text'],
.form-group input[type='number'],
.form-group input[type='file'],
.form-group select {
  width: 100%;
  min-height: 52px;
  padding: 0 16px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  font-size: 15px;
  background: #fff;
  color: #0f172a;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-group input[type='file'] {
  padding: 12px 16px;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 22px;
  padding: 8px 0;
}

.checkbox-item,
.checkbox-inline {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.checkbox-item input,
.checkbox-inline input {
  width: 18px;
  height: 18px;
}

.image-preview {
  width: 100%;
  max-width: 240px;
  border: 1px solid #cbd5e1;
  border-radius: 18px;
  overflow: hidden;
  background: #f8fafc;
}

.image-preview img {
  display: block;
  width: 100%;
  height: 240px;
  object-fit: cover;
}

.message {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
}

.error-message {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.success-message {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.save-btn {
  margin-top: 24px;
  min-width: 160px;
  height: 52px;
  padding: 0 24px;
  border: none;
  border-radius: 14px;
  background: #0f172a;
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.2s ease;
}

.save-btn:hover {
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .page-card {
    padding: 22px;
    border-radius: 20px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 26px;
  }
}
</style>