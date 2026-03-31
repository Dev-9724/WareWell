<template>
  <div class="landing-page">
    <section class="hero-card">
      <p class="eyebrow">WareWell</p>
      <h1>Context-Aware Wardrobe Recommendation</h1>
      <p class="subtitle">
        Sign up once, log in once, and manage your wardrobe, recommendations,
        feedback, evaluation, and explanations without re-entering your user id.
      </p>

      <div class="actions">
        <router-link class="primary-btn" to="/signup">Create account</router-link>
        <router-link class="secondary-btn" to="/login">Login</router-link>
      </div>
    </section>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #f5f8fc;
}
.hero-card {
  width: min(900px, 100%);
  background: white;
  border: 1px solid #e4e9f2;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 50px rgba(8, 18, 37, 0.06);
}
.eyebrow {
  margin: 0 0 12px;
  color: #1dd1a1;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
h1 {
  margin: 0 0 14px;
  font-size: clamp(2rem, 4vw, 3.4rem);
}
.subtitle {
  margin: 0 0 24px;
  color: #66758f;
  line-height: 1.7;
}
.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.primary-btn,
.secondary-btn {
  text-decoration: none;
  padding: 12px 18px;
  border-radius: 12px;
  font-weight: 700;
}
.primary-btn {
  background: #081225;
  color: white;
}
.secondary-btn {
  background: #eef5ff;
  color: #26446e;
}
</style>