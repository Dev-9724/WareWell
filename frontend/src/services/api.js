const BASE_URL = 'http://127.0.0.1:8000'

async function handleResponse(response) {
    if (!response.ok) {
        const text = await response.text()
        throw new Error(text || 'API request failed')
    }

    return response.json()
}

export async function getLatestWeather() {
    const response = await fetch(`${BASE_URL}/weather/latest`)
    return handleResponse(response)
}

export async function getWardrobeItems() {
    const response = await fetch(`${BASE_URL}/wardrobe/items`)
    return handleResponse(response)
}

export async function addWardrobeItem(item) {
    const response = await fetch(`${BASE_URL}/wardrobe/items`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(item),
    })

    return handleResponse(response)
}

export async function getRankedOutfits(userId, occasion = 'office', topK = 5, maxOutfits = 20) {
    const url =
        `${BASE_URL}/recommend/ranked-outfits` +
        `?user_id=${encodeURIComponent(userId)}` +
        `&occasion=${encodeURIComponent(occasion)}` +
        `&top_k=${topK}` +
        `&max_outfits=${maxOutfits}`

    const response = await fetch(url, {
        method: 'POST',
    })

    return handleResponse(response)
}

export async function submitFeedback(payload) {
    const response = await fetch(`${BASE_URL}/feedback/submit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
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

export async function getEvaluationComparison(
  userId,
  occasion = 'office',
  topK = 5,
  maxOutfits = 20
) {
  const url =
    `${BASE_URL}/evaluation/compare` +
    `?user_id=${encodeURIComponent(userId)}` +
    `&occasion=${encodeURIComponent(occasion)}` +
    `&top_k=${topK}` +
    `&max_outfits=${maxOutfits}`

  const response = await fetch(url, {
    method: 'POST',
  })

  return handleResponse(response)
}

export async function getExplanations(
  userId,
  occasion = 'office',
  topK = 5,
  maxOutfits = 20
) {
  const url =
    `${BASE_URL}/recommend/explanations` +
    `?user_id=${encodeURIComponent(userId)}` +
    `&occasion=${encodeURIComponent(occasion)}` +
    `&top_k=${topK}` +
    `&max_outfits=${maxOutfits}`

  const response = await fetch(url, {
    method: 'POST',
  })

  return handleResponse(response)
}