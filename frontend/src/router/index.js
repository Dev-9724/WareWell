import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import WardrobePage from '../pages/WardrobePage.vue'
import AddItemPage from '../pages/AddItemPage.vue'
import RecommendationsPage from '../pages/RecommendationsPage.vue'
import FeedbackPage from '../pages/FeedbackPage.vue'
import EvaluationPage from '../pages/EvaluationPage.vue'
import ExplanationsPage from '../pages/ExplanationsPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/wardrobe', name: 'wardrobe', component: WardrobePage },
  { path: '/add-item', name: 'add-item', component: AddItemPage },
  { path: '/recommendations', name: 'recommendations', component: RecommendationsPage },
  { path: '/feedback', name: 'feedback', component: FeedbackPage },
  { path: '/evaluation', name: 'evaluation', component: EvaluationPage },
  { path: '/explanations', name: 'explanations', component: ExplanationsPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router