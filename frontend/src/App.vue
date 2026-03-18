<template>
  <div class="app-container">
    <header class="app-header">
      <h1>WareWell</h1>
      <nav>
        <router-link to="/">Home</router-link>
        <router-link to="/wardrobe">Wardrobe</router-link>
        <router-link to="/add-item">Add Item</router-link>
        <router-link to="/recommendations">Recommendations</router-link>
        <router-link to="/feedback">Feedback</router-link>
        <router-link to="/evaluation">Evaluation</router-link>
        <router-link to="/explanations">Explanations</router-link>
      </nav>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f8fafc;
  color: #1f2937;
  font-family: Arial, sans-serif;
}

.app-header {
  background: #111827;
  color: white;
  padding: 20px;
}

.app-header h1 {
  margin: 0 0 12px 0;
}

nav {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

nav a {
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 500;
}

nav a.router-link-active {
  color: #22c55e;
}

.app-main {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>