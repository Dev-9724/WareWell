<template>
  <div class="app-shell">
    <header v-if="isAuthenticated" class="topbar">
      <div class="brand-wrap">
        <router-link to="/dashboard" class="brand-link">WareWell</router-link>
        <span class="tagline">Context-Aware Wardrobe Recommendation</span>
      </div>

      <nav class="nav-links">
        <router-link to="/wardrobe">Wardrobe</router-link>
        <router-link to="/add-item">Add Item</router-link>
        <router-link to="/recommendations">Recommendations</router-link>
        <router-link to="/evaluation">Evaluation</router-link>
        <router-link to="/explanations">Explanations</router-link>
      </nav>

      <div class="user-actions">
        <span class="username">{{ currentUser?.username }}</span>
        <button class="logout-btn" @click="handleLogout">Logout</button>
      </div>
    </header>

    <main class="page-wrap">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth'

const router = useRouter()
const { currentUser, isAuthenticated, logout } = useAuth()

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f5f8fc;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: white;
  border-bottom: 1px solid #e4e9f2;
  padding: 14px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.brand-wrap {
  display: flex;
  flex-direction: column;
}

.brand-link {
  text-decoration: none;
  color: #081225;
  font-size: 1.2rem;
  font-weight: 800;
}

.tagline {
  color: #6c7890;
  font-size: 0.85rem;
}

.nav-links {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.nav-links a {
  text-decoration: none;
  color: #29466f;
  font-weight: 600;
}

.nav-links a.router-link-active {
  color: #081225;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: #5d6d86;
  font-weight: 700;
}

.logout-btn {
  border: none;
  background: #081225;
  color: white;
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.page-wrap {
  padding: 24px;
}

@media (max-width: 820px) {
  .topbar {
    align-items: flex-start;
  }

  .page-wrap {
    padding: 16px;
  }
}
</style>