import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import api from '../api'

vi.mock('axios')

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('creates axios instance with correct base URL', () => {
    expect(api.defaults.baseURL).toBe(import.meta.env.VITE_API_URL || 'http://localhost:5001/api')
  })

  it('adds authorization header when token exists', async () => {
    const token = 'test-token'
    localStorage.setItem('token', token)
    
    api.interceptors.request.handlers[0].fulfilled({ headers: {} })
    
    const config = await api.interceptors.request.handlers[0].fulfilled({ headers: {} })
    expect(config.headers.Authorization).toBe(`Bearer ${token}`)
  })

  it('does not add authorization header when no token', async () => {
    const config = await api.interceptors.request.handlers[0].fulfilled({ headers: {} })
    expect(config.headers.Authorization).toBeUndefined()
  })

  it('handles successful responses', async () => {
    const responseData = { data: 'test' }
    const response = { data: responseData }
    
    const result = await api.interceptors.response.handlers[0].fulfilled(response)
    expect(result).toEqual(responseData)
  })

  it('handles 401 errors by removing token and redirecting', async () => {
    const error = {
      response: { status: 401 },
      config: { url: '/some-endpoint' }
    }
    
    // Mock window.location
    delete window.location
    window.location = { href: '' }
    
    localStorage.setItem('token', 'expired-token')
    
    try {
      await api.interceptors.response.handlers[0].rejected(error)
    } catch (e) {
      expect(localStorage.getItem('token')).toBeNull()
      expect(window.location.href).toBe('/login')
    }
  })

  it('does not redirect to login for auth endpoints', async () => {
    const error = {
      response: { status: 401 },
      config: { url: '/auth/login' }
    }
    
    delete window.location
    window.location = { href: '' }
    
    try {
      await api.interceptors.response.handlers[0].rejected(error)
    } catch (e) {
      expect(window.location.href).toBe('')
    }
  })

  it('passes through non-401 errors', async () => {
    const error = {
      response: { status: 500, data: { error: 'Server error' } }
    }
    
    try {
      await api.interceptors.response.handlers[0].rejected(error)
    } catch (e) {
      expect(e).toBe(error)
    }
  })

  it('handles network errors', async () => {
    const error = new Error('Network Error')
    
    try {
      await api.interceptors.response.handlers[0].rejected(error)
    } catch (e) {
      expect(e).toBe(error)
    }
  })

  it('makes GET requests', async () => {
    const mockData = { id: 1, name: 'Test' }
    axios.get = vi.fn().mockResolvedValue({ data: mockData })
    
    const result = await api.get('/test')
    
    expect(axios.get).toHaveBeenCalledWith('/test', undefined)
    expect(result).toEqual(mockData)
  })

  it('makes POST requests', async () => {
    const postData = { name: 'New Item' }
    const mockResponse = { id: 1, ...postData }
    axios.post = vi.fn().mockResolvedValue({ data: mockResponse })
    
    const result = await api.post('/test', postData)
    
    expect(axios.post).toHaveBeenCalledWith('/test', postData, undefined)
    expect(result).toEqual(mockResponse)
  })

  it('makes PUT requests', async () => {
    const updateData = { name: 'Updated Item' }
    const mockResponse = { id: 1, ...updateData }
    axios.put = vi.fn().mockResolvedValue({ data: mockResponse })
    
    const result = await api.put('/test/1', updateData)
    
    expect(axios.put).toHaveBeenCalledWith('/test/1', updateData, undefined)
    expect(result).toEqual(mockResponse)
  })

  it('makes DELETE requests', async () => {
    const mockResponse = { message: 'Deleted successfully' }
    axios.delete = vi.fn().mockResolvedValue({ data: mockResponse })
    
    const result = await api.delete('/test/1')
    
    expect(axios.delete).toHaveBeenCalledWith('/test/1', undefined)
    expect(result).toEqual(mockResponse)
  })
})