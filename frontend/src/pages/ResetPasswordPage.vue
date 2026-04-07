<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="eyebrow">Account Recovery</p>
      <h1>Reset Password</h1>
      <p class="subtitle">
        Enter your new password below to complete the password reset.
      </p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <label class="field">
          <span>New Password</span>
          <input
            v-model="newPassword"
            type="password"
            placeholder="Enter new password"
            required
            minlength="6"
          />
        </label>

        <label class="field">
          <span>Confirm New Password</span>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm new password"
            required
            minlength="6"
          />
        </label>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Resetting...' : 'Reset Password' }}
        </button>
      </form>

      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <router-link to="/login" class="back-link">Back to Login</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resetPassword } from '../services/api.js'               

const route = useRoute()
const router = useRouter()

const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const message = ref('')
const errorMessage = ref('')

const token = computed(() => String(route.query.token || '').trim())

async function handleSubmit() {
  errorMessage.value = ''
  message.value = ''

  if (!token.value) {
    errorMessage.value = 'Reset token is missing from the URL.'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    const response = await resetPassword({
      token: token.value,
      new_password: newPassword.value,
    })

    message.value = response.message || 'Password reset successful.'

    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to reset password.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #f8fafc;
}

.auth-card {
  width: 100%;
  max-width: 460px;
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
}

h1 {
  margin: 0 0 10px;
  font-size: 2rem;
  color: #0f172a;
}

.subtitle {
  margin: 0 0 24px;
  color: #475569;
  line-height: 1.6;
}

.auth-form {
  display: grid;
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
}

.field span {
  font-weight: 600;
  color: #334155;
}

.field input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  font-size: 1rem;
}

button {
  border: none;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  background: #0f172a;
  color: white;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.success-message {
  margin-top: 18px;
  color: #15803d;
  font-weight: 600;
}

.error-message {
  margin-top: 18px;
  color: #dc2626;
  font-weight: 600;
}

.back-link {
  display: inline-block;
  margin-top: 20px;
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}

.back-link:hover {
  text-decoration: underline;
}
</style>