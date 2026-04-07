const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const STORAGE_KEY = 'warewell_auth_user'

function getStoredUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (error) {
    console.error('Failed to parse stored user:', error)
    return null
  }
}

export function getCurrentUserId() {
  return getStoredUser()?.id || ''
}

export function getStoredUsername() {
  return getStoredUser()?.username || ''
}

function buildApiError(text, fallback = 'API request failed') {
  try {
    const parsed = JSON.parse(text)
    if (typeof parsed?.detail === 'string') return parsed.detail
    if (Array.isArray(parsed?.detail)) {
      return parsed.detail.map((item) => item?.msg || JSON.stringify(item)).join(', ')
    }
  } catch (_) {
    // ignore json parse failures
  }

  return text || fallback
}

async function handleResponse(response) {
  if (!response.ok) {
    const text = await response.text()
    throw new Error(buildApiError(text))
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export async function signupUser(payload) {
  const response = await fetch(`${BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return handleResponse(response)
}

export async function loginUser(payload) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return handleResponse(response)
}

export async function forgotPassword(payload) {
  const response = await fetch(`${BASE_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return handleResponse(response)
}

export async function resetPassword(payload) {
  const response = await fetch(`${BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return handleResponse(response)
}

export async function getCurrentUser(userId = getCurrentUserId()) {
  const response = await fetch(`${BASE_URL}/auth/me/${encodeURIComponent(userId)}`)
  return handleResponse(response)
}

export async function fetchCurrentWeather(city) {
  const resolvedCity = (city || '').trim()

  if (!resolvedCity) {
    throw new Error('Please enter a location.')
  }

  const response = await fetch(
    `${BASE_URL}/weather/current?city=${encodeURIComponent(resolvedCity)}`
  )

  return handleResponse(response)
}

export async function getLatestWeather() {
  const response = await fetch(`${BASE_URL}/weather/latest`)
  return handleResponse(response)
}

export async function fetchWeatherWithFallback(city) {
  try {
    const liveWeather = await fetchCurrentWeather(city)
    return {
      ...liveWeather,
      fallback_used: false,
    }
  } catch (liveError) {
    console.warn('Live weather fetch failed, using latest snapshot instead:', liveError)

    try {
      const snapshotWeather = await getLatestWeather()
      return {
        ...snapshotWeather,
        fallback_used: true,
        fallback_reason: liveError?.message || 'Live weather fetch failed',
      }
    } catch (snapshotError) {
      const causeError =
        liveError instanceof Error
          ? liveError
          : snapshotError instanceof Error
            ? snapshotError
            : undefined

      throw new Error(
        (liveError?.message || snapshotError?.message || 'Unable to fetch weather data.'),
        causeError ? { cause: causeError } : undefined
      )
    }
  }
}

export async function getWardrobeItems(userId = getCurrentUserId()) {
  if (!userId) {
    throw new Error('No logged-in user found. Please log in again.')
  }

  const response = await fetch(
    `${BASE_URL}/wardrobe/items?user_id=${encodeURIComponent(userId)}`
  )
  return handleResponse(response)
}

export async function addWardrobeItem(itemData) {
  const response = await fetch(`${BASE_URL}/wardrobe/items`, {
    method: 'POST',
    body: itemData,
  })

  return handleResponse(response)
}

export async function deleteWardrobeItem(itemId) {
  const response = await fetch(`${BASE_URL}/wardrobe/items/${itemId}`, {
    method: 'DELETE',
  })

  return handleResponse(response)
}

export async function getRankedOutfits(
  occasion = 'office',
  topK = 5,
  maxOutfits = 20,
  userId = getCurrentUserId()
) {
  if (!userId) {
    throw new Error('No logged-in user found. Please log in again.')
  }

  const url =
    `${BASE_URL}/recommend/ranked-outfits` +
    `?user_id=${encodeURIComponent(userId)}` +
    `&occasion=${encodeURIComponent(occasion)}` +
    `&top_k=${topK}` +
    `&max_outfits=${maxOutfits}`

  const response = await fetch(url, { method: 'POST' })
  return handleResponse(response)
}

export async function getExplanations(
  occasion = 'office',
  topK = 5,
  maxOutfits = 20,
  userId = getCurrentUserId()
) {
  if (!userId) {
    throw new Error('No logged-in user found. Please log in again.')
  }

  const url =
    `${BASE_URL}/recommend/explanations` +
    `?user_id=${encodeURIComponent(userId)}` +
    `&occasion=${encodeURIComponent(occasion)}` +
    `&top_k=${topK}` +
    `&max_outfits=${maxOutfits}`

  const response = await fetch(url, { method: 'POST' })
  return handleResponse(response)
}

export async function getEvaluationComparison(
  occasion = 'office',
  topK = 5,
  maxOutfits = 20,
  userId = getCurrentUserId()
) {
  if (!userId) {
    throw new Error('No logged-in user found. Please log in again.')
  }

  const url =
    `${BASE_URL}/evaluation/compare` +
    `?user_id=${encodeURIComponent(userId)}` +
    `&occasion=${encodeURIComponent(occasion)}` +
    `&top_k=${topK}` +
    `&max_outfits=${maxOutfits}`

  const response = await fetch(url, { method: 'POST' })
  return handleResponse(response)
}

export async function submitFeedback(payload) {
  const finalPayload = {
    ...payload,
    user_id: payload.user_id || getCurrentUserId(),
  }

  const response = await fetch(`${BASE_URL}/feedback/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(finalPayload),
  })

  return handleResponse(response)
}

export async function getCurrentWeights() {
  const response = await fetch(`${BASE_URL}/feedback/weights`)
  return handleResponse(response)
}

export async function getFeedbackLogs() {
  const response = await fetch(`${BASE_URL}/feedback/logs`)
  return handleResponse(response)
}

export function getImageUrl(imagePath) {
  if (!imagePath) return ''

  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }

  if (imagePath.startsWith('/')) {
    return `${BASE_URL}${imagePath}`
  }

  return `${BASE_URL}/${imagePath}`
}