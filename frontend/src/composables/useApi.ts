const BASE = '/api'

export async function apiFetch<T = any>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...opts.headers as any },
    ...opts,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || res.statusText)
  }
  return res.json()
}

export async function apiUpload<T = any>(path: string, file: File, fields: Record<string, string> = {}): Promise<T> {
  const form = new FormData()
  form.append('file', file)
  for (const [k, v] of Object.entries(fields)) {
    form.append(k, v)
  }
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || res.statusText)
  }
  return res.json()
}
