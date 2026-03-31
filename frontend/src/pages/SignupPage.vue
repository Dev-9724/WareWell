<template>
  <div class="auth-page">
    <form class="auth-card" @submit.prevent="handleSignup">
      <p class="eyebrow">Get started</p>
      <h1>Create account</h1>

      <label>Username</label>
      <input v-model="form.username" type="text" required />

      <label>Email</label>
      <input v-model="form.email" type="email" required />

      <label>Password</label>
      <input v-model="form.password" type="password" required />

      <p v-if="error" class="error-text">{{ error }}</p>

      <button class="primary-btn" :disabled="loading">
        {{ loading ? 'Creating account...' : 'Sign up' }}
      </button>

      <p class="footer-text">
        Already have an account?
        <router-link to="/login">Login</router-link>
      </p>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { signupUser } from '../services/api'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { setUser } = useAuth()

const form = reactive({
  username: '',
  email: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

async function handleSignup() {
  loading.value = true
  error.value = ''

  try {
    const createdUser = await signupUser(form)
    setUser(createdUser)
    router.push('/wardrobe')
  } catch (err) {
    console.error(err)
    error.value = 'Signup failed. Try a different email or username.'
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
  background: #f5f8fc;
}
.auth-card {
  width: min(460px, 100%);
  background: white;
  border: 1px solid #e4e9f2;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 50px rgba(8, 18, 37, 0.06);
  display: grid;
  gap: 12px;
}
.eyebrow {
  margin: 0;
  color: #1dd1a1;
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.08em;
}
h1 {
  margin: 0 0 10px;
}
label {
  font-weight: 700;
  color: #31425f;
}
input {
  padding: 12px 14px;
  border: 1px solid #d8e1ee;
  border-radius: 12px;
}
.primary-btn {
  margin-top: 8px;
  border: none;
  background: #081225;
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}
.error-text {
  color: #b42318;
  margin: 0;
}
.footer-text {
  margin: 8px 0 0;
  color: #66758f;
}
</style>