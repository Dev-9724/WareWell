<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="eyebrow">Account Recovery</p>
      <h1>Forgot Password</h1>
      <p class="subtitle">
        Enter your email address and generate a reset link for your account.
      </p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <label class="field">
          <span>Email</span>
          <input
            v-model.trim="email"
            type="email"
            placeholder="Enter your email"
            required
          />
        </label>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Generating...' : 'Generate Reset Link' }}
        </button>
      </form>

      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div v-if="resetLink" class="token-box">
        <p class="token-title">Local testing reset link</p>
        <a :href="resetLink">{{ resetLink }}</a>
      </div>

      <router-link to="/login" class="back-link">Back to Login</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { forgotPassword } from '../services/api.js'

const email = ref('')
const loading = ref(false)
const message = ref('')
const errorMessage = ref('')

async function handleSubmit() {
  loading.value = true
  message.value = ''
  errorMessage.value = ''

  try {
    const response = await forgotPassword({ email: email.value })
    message.value =
      response.message || 'If your email exists, a password reset email has been sent.'
  } catch (error) {
    errorMessage.value = error.message || 'Failed to send reset email.'
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

.token-box {
  margin-top: 18px;
  padding: 14px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  word-break: break-word;
}

.token-title {
  margin: 0 0 8px;
  font-weight: 700;
  color: #1e3a8a;
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