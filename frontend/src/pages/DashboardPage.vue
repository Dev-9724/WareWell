<template>
  <div class="dashboard-page">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">Welcome to WareWell</p>
        <h1>Hello, {{ currentUser?.username || 'User' }}</h1>
        <p class="subtitle">
          Manage your wardrobe, generate outfit recommendations, compare evaluation
          results, and explore explanation details from one central dashboard.
        </p>

        <div class="hero-actions">
          <router-link to="/recommendations" class="primary-btn">
            Generate Outfit
          </router-link>
          <router-link to="/wardrobe" class="secondary-btn">
            Open Wardrobe
          </router-link>
        </div>
      </div>

      <div class="hero-side">
        <div class="hero-badge">Explainable Hybrid System</div>

        <div class="mini-stats">
          <div class="mini-stat">
            <span class="mini-label">Core Approach</span>
            <strong>Constraint + Ranking</strong>
          </div>
          <div class="mini-stat">
            <span class="mini-label">Context Used</span>
            <strong>Weather + Occasion</strong>
          </div>
          <div class="mini-stat">
            <span class="mini-label">Output</span>
            <strong>Best Outfit + Explanation</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-grid">
      <div class="stat-card">
        <span class="stat-label">Context-Aware</span>
        <h3>Filters items using weather and occasion before ranking.</h3>
      </div>

      <div class="stat-card">
        <span class="stat-label">Explainable</span>
        <h3>Shows why the selected outfit was chosen.</h3>
      </div>

      <div class="stat-card">
        <span class="stat-label">Evaluation Ready</span>
        <h3>Supports comparison between baseline and hybrid models.</h3>
      </div>
    </section>

    <section class="grid-two">
      <div class="panel-card">
        <div class="panel-header">
          <h2>How WareWell Works</h2>
          <span class="tag">System Pipeline</span>
        </div>

        <div class="pipeline">
          <div class="pipeline-step">
            <span class="step-number">1</span>
            <div>
              <strong>Context Input</strong>
              <p>Read weather and occasion details.</p>
            </div>
          </div>

          <div class="pipeline-line"></div>

          <div class="pipeline-step">
            <span class="step-number">2</span>
            <div>
              <strong>Constraint Filtering</strong>
              <p>Remove unsuitable wardrobe items.</p>
            </div>
          </div>

          <div class="pipeline-line"></div>

          <div class="pipeline-step">
            <span class="step-number">3</span>
            <div>
              <strong>Compatibility Check</strong>
              <p>Match clothing pieces that work together.</p>
            </div>
          </div>

          <div class="pipeline-line"></div>

          <div class="pipeline-step">
            <span class="step-number">4</span>
            <div>
              <strong>Scoring Module</strong>
              <p>Rank outfits using multiple criteria.</p>
            </div>
          </div>

          <div class="pipeline-line"></div>

          <div class="pipeline-step">
            <span class="step-number">5</span>
            <div>
              <strong>Best Outfit</strong>
              <p>Return the highest-ranked explainable result.</p>
            </div>
          </div>
        </div>

        <div class="helper-box">
          The dashboard summarises the full recommendation workflow: context is collected
          first, infeasible outfits are removed, compatible combinations are checked,
          remaining outfits are scored, and the best result is returned with explanation.
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h2>Why This System Is Useful</h2>
          <span class="tag">Project Value</span>
        </div>

        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">✓</div>
            <div>
              <h3>Reduces decision fatigue</h3>
              <p>Helps users choose outfits faster from their own wardrobe.</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">✓</div>
            <div>
              <h3>Improves transparency</h3>
              <p>Explains why each outfit recommendation was selected.</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">✓</div>
            <div>
              <h3>Supports sustainability</h3>
              <p>Encourages better wardrobe use instead of more shopping.</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">✓</div>
            <div>
              <h3>Academic evaluation ready</h3>
              <p>Lets you compare baseline and hybrid recommendation performance.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="dashboard-grid">
      <router-link to="/wardrobe" class="dashboard-card">
        <h3>Wardrobe</h3>
        <p>View, filter, and manage your clothing collection.</p>
      </router-link>

      <router-link to="/add-item" class="dashboard-card">
        <h3>Add Item</h3>
        <p>Add new wardrobe items quickly with simple user-friendly fields.</p>
      </router-link>

      <router-link to="/recommendations" class="dashboard-card">
        <h3>Recommendations</h3>
        <p>Generate ranked outfits based on wardrobe data and user context.</p>
      </router-link>

      <router-link to="/evaluation" class="dashboard-card">
        <h3>Evaluation</h3>
        <p>Compare baseline, filtered, and hybrid recommendation results.</p>
      </router-link>

      <router-link to="/explanations" class="dashboard-card">
        <h3>Explanations</h3>
        <p>Inspect the reasoning behind outfit selection and ranking.</p>
      </router-link>

      <div class="dashboard-card tip-card">
        <h3>Quick Tip</h3>
        <p>
          Add a few tops, bottoms, shoes, and outerwear items first to get stronger
          outfit recommendations.
        </p>
      </div>
    </section>

    <section class="bottom-grid">
      <div class="panel-card">
        <div class="panel-header">
          <h2>Recommended Flow</h2>
          <span class="tag">For Users</span>
        </div>

        <div class="journey-steps">
          <div class="journey-step">
            <strong>1. Add wardrobe items</strong>
            <p>Start by building your clothing collection.</p>
          </div>
          <div class="journey-step">
            <strong>2. Select context</strong>
            <p>Choose weather and occasion information.</p>
          </div>
          <div class="journey-step">
            <strong>3. Generate outfit</strong>
            <p>Let WareWell rank the best valid combinations.</p>
          </div>
          <div class="journey-step">
            <strong>4. Review explanation</strong>
            <p>See why the final result was selected.</p>
          </div>
        </div>
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <h2>Quick Actions</h2>
          <span class="tag">Navigation</span>
        </div>

        <div class="action-list">
          <router-link to="/add-item" class="action-tile">
            <strong>Add your next item</strong>
            <span>Expand your wardrobe data</span>
          </router-link>

          <router-link to="/recommendations" class="action-tile">
            <strong>Generate today’s outfit</strong>
            <span>Use the ranking engine</span>
          </router-link>

          <router-link to="/evaluation" class="action-tile">
            <strong>Review evaluation results</strong>
            <span>Compare recommendation models</span>
          </router-link>

          <router-link to="/explanations" class="action-tile">
            <strong>Open explanation page</strong>
            <span>Inspect the pipeline decisions</span>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { currentUser } = useAuth()
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 24px;
}

.hero-card,
.panel-card,
.dashboard-card,
.stat-card {
  background: white;
  border: 1px solid #e3e8f2;
  border-radius: 20px;
  box-shadow: 0 12px 30px rgba(8, 18, 37, 0.04);
}

.hero-card {
  padding: 28px;
  display: grid;
  grid-template-columns: 1.4fr 0.8fr;
  gap: 24px;
  align-items: center;
}

.hero-copy {
  display: grid;
  gap: 14px;
}

.eyebrow {
  margin: 0;
  color: #1dd1a1;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-card h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  color: #081225;
}

.subtitle {
  margin: 0;
  color: #6a7790;
  line-height: 1.7;
  max-width: 820px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.primary-btn,
.secondary-btn {
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.primary-btn {
  background: #081225;
  color: white;
}

.secondary-btn {
  background: #eef5ff;
  color: #31507f;
  border: 1px solid #d6dfec;
}

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-2px);
}

.hero-side {
  display: grid;
  gap: 14px;
}

.hero-badge {
  justify-self: start;
  background: #081225;
  color: white;
  padding: 12px 16px;
  border-radius: 999px;
  font-weight: 700;
}

.mini-stats {
  display: grid;
  gap: 12px;
}

.mini-stat {
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 16px;
  padding: 14px 16px;
  display: grid;
  gap: 4px;
}

.mini-label {
  font-size: 0.82rem;
  color: #6a7790;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  padding: 20px;
}

.stat-label {
  display: inline-block;
  margin-bottom: 10px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #eef5ff;
  color: #31507f;
  font-size: 0.8rem;
  font-weight: 700;
}

.stat-card h3 {
  margin: 0;
  color: #081225;
  font-size: 1.05rem;
  line-height: 1.5;
}

.grid-two,
.bottom-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.panel-card {
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0;
  color: #081225;
}

.tag {
  background: #eef5ff;
  color: #31507f;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  white-space: nowrap;
}

.pipeline {
  display: grid;
  gap: 10px;
}

.pipeline-step {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 14px;
}

.pipeline-step strong {
  display: block;
  margin-bottom: 4px;
  color: #081225;
}

.pipeline-step p {
  margin: 0;
  color: #6a7790;
  line-height: 1.5;
}

.step-number {
  min-width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #081225;
  color: white;
  font-weight: 800;
  font-size: 0.9rem;
}

.pipeline-line {
  width: 2px;
  height: 14px;
  background: #d9e2ef;
  margin-left: 15px;
}

.helper-box {
  margin-top: 18px;
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 16px;
  color: #4b5870;
  line-height: 1.7;
}

.feature-list {
  display: grid;
  gap: 14px;
}

.feature-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px;
  border-radius: 14px;
  background: #f7f9fc;
  border: 1px solid #e7edf5;
}

.feature-icon {
  min-width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #dff8f1;
  color: #08a87a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.feature-item h3 {
  margin: 0 0 6px;
  font-size: 1rem;
  color: #081225;
}

.feature-item p {
  margin: 0;
  color: #6a7790;
  line-height: 1.6;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.dashboard-card {
  text-decoration: none;
  color: inherit;
  padding: 22px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(8, 18, 37, 0.08);
}

.dashboard-card h3 {
  margin: 0 0 10px;
  color: #081225;
}

.dashboard-card p {
  margin: 0;
  color: #6a7790;
  line-height: 1.6;
}

.tip-card {
  background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
}

.journey-steps,
.action-list {
  display: grid;
  gap: 14px;
}

.journey-step,
.action-tile {
  background: #f7f9fc;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 14px;
}

.journey-step strong,
.action-tile strong {
  display: block;
  margin-bottom: 6px;
  color: #081225;
}

.journey-step p,
.action-tile span {
  margin: 0;
  color: #6a7790;
  line-height: 1.5;
}

.action-tile {
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.action-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(8, 18, 37, 0.06);
}

@media (max-width: 1100px) {
  .hero-card,
  .grid-two,
  .bottom-grid,
  .stats-grid,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .hero-card,
  .panel-card,
  .dashboard-card,
  .stat-card {
    padding: 18px;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>