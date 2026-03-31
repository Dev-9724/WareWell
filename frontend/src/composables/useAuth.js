import { computed, ref } from 'vue'

const STORAGE_KEY = 'warewell_auth_user'

const user = ref(loadStoredUser())

function loadStoredUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (error) {
    console.error('Failed to read auth user from storage:', error)
    return null
  }
}

function persistUser(nextUser) {
  user.value = nextUser

  if (nextUser) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser))
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const currentUser = computed(() => user.value)

  function setUser(nextUser) {
    persistUser(nextUser)
  }

  function logout() {
    persistUser(null)
  }

  function getUserId() {
    return user.value?.id || ''
  }

  function getUsername() {
    return user.value?.username || ''
  }

  return {
    currentUser,
    isAuthenticated,
    setUser,
    logout,
    getUserId,
    getUsername,
  }
}