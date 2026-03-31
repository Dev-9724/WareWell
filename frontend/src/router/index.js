import { createRouter, createWebHistory } from 'vue-router'

import LandingPage from '../pages/LandingPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import SignupPage from '../pages/SignupPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import WardrobePage from '../pages/WardrobePage.vue'
import AddItemPage from '../pages/AddItemPage.vue'
import RecommendationsPage from '../pages/RecommendationsPage.vue'
import EvaluationPage from '../pages/EvaluationPage.vue'
import ExplanationsPage from '../pages/ExplanationsPage.vue'
import FeedbackPage from '../pages/FeedbackPage.vue'
import BaselineComparisonPage from '../pages/BaselineComparisonPage.vue'

const routes = [
  { path: '/', name: 'landing', component: LandingPage, meta: { public: true } },
  { path: '/login', name: 'login', component: LoginPage, meta: { public: true } },
  { path: '/signup', name: 'signup', component: SignupPage, meta: { public: true } },
  { path: '/dashboard', name: 'dashboard', component: DashboardPage },
  { path: '/wardrobe', name: 'wardrobe', component: WardrobePage },
  { path: '/add-item', name: 'add-item', component: AddItemPage },
  { path: '/recommendations', name: 'recommendations', component: RecommendationsPage },
  { path: '/evaluation', name: 'evaluation', component: EvaluationPage },
  { path: '/explanations', name: 'explanations', component: ExplanationsPage },
  { path: '/feedback', name: 'feedback', component: FeedbackPage },
  { path: '/baseline-comparison', name: 'baseline-comparison', component: BaselineComparisonPage, }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const storedUser = localStorage.getItem('warewell_auth_user')
  const isLoggedIn = !!storedUser
  const isPublic = !!to.meta.public

  if (!isPublic && !isLoggedIn) {
    return '/login'
  }

  if (isLoggedIn && (to.path === '/login' || to.path === '/signup' || to.path === '/')) {
    return '/dashboard'
  }

  return true
})

export default router