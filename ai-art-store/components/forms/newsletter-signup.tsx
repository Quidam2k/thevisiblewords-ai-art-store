'use client'

import { useState } from 'react'
import { validateEmail } from '@/lib/utils'

interface NewsletterSignupProps {
  compact?: boolean
}

export function NewsletterSignup({ compact = false }: NewsletterSignupProps) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateEmail(email)) {
      setMessage('Please enter a valid email address')
      setIsSuccess(false)
      return
    }

    setLoading(true)
    setMessage('')

    try {
      // TODO: Implement newsletter signup API
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })

      if (response.ok) {
        setMessage('Thanks for subscribing!')
        setIsSuccess(true)
        setEmail('')
      } else {
        throw new Error('Failed to subscribe')
      }
    } catch (error) {
      setMessage('Something went wrong. Please try again.')
      setIsSuccess(false)
    } finally {
      setLoading(false)
    }
  }

  if (compact) {
    return (
      <div className="w-full max-w-sm">
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Subscribing...' : 'Subscribe'}
          </button>
        </form>
        {message && (
          <p className={`text-sm mt-2 ${isSuccess ? 'text-green-400' : 'text-red-400'}`}>
            {message}
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email address"
          className="flex-1 px-4 py-3 border border-purple-300 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent text-gray-900 placeholder-gray-500"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
        >
          {loading ? 'Subscribing...' : 'Subscribe'}
        </button>
      </form>
      
      {message && (
        <p className={`text-sm mt-3 ${isSuccess ? 'text-purple-100' : 'text-red-200'}`}>
          {message}
        </p>
      )}
      
      <p className="text-xs text-purple-100 mt-3">
        No spam, unsubscribe at any time. We respect your privacy.
      </p>
    </div>
  )
}