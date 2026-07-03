export function toDisplayDate(apiDate) {
  if (!apiDate) return ''
  const parts = apiDate.split('-')
  if (parts.length !== 3) return apiDate
  return `${parts[2]}-${parts[1]}-${parts[0]}`
}

export function toApiDate(displayDate) {
  if (!displayDate) return null
  const parts = displayDate.split('-')
  if (parts.length !== 3) return null
  return `${parts[2]}-${parts[1]}-${parts[0]}`
}

export function parseDutchDate(displayDate) {
  if (!displayDate) return null
  const parts = displayDate.split('-')
  if (parts.length !== 3) return null
  return new Date(`${parts[2]}-${parts[1]}-${parts[0]}`)
}
