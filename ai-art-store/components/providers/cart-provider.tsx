'use client'

import { createContext, useContext, useReducer, useEffect } from 'react'
import { CartItem, Cart } from '@/types'

interface CartState {
  items: CartItem[]
  isLoading: boolean
}

type CartAction = 
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_CART'; payload: CartItem[] }
  | { type: 'SET_LOADING'; payload: boolean }

interface CartContextType extends Cart {
  addItem: (item: CartItem) => void
  removeItem: (id: string) => void
  updateQuantity: (id: string, quantity: number) => void
  clearCart: () => void
  isLoading: boolean
}

const CartContext = createContext<CartContextType | undefined>(undefined)

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM':
      const existingItem = state.items.find(item => 
        item.productId === action.payload.productId && 
        item.variant.id === action.payload.variant.id
      )
      
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === existingItem.id
              ? { ...item, quantity: item.quantity + action.payload.quantity }
              : item
          ),
        }
      }
      
      return {
        ...state,
        items: [...state.items, action.payload],
      }

    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload),
      }

    case 'UPDATE_QUANTITY':
      if (action.payload.quantity <= 0) {
        return {
          ...state,
          items: state.items.filter(item => item.id !== action.payload.id),
        }
      }
      
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        ),
      }

    case 'CLEAR_CART':
      return {
        ...state,
        items: [],
      }

    case 'LOAD_CART':
      return {
        ...state,
        items: action.payload,
      }

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }

    default:
      return state
  }
}

function calculateTax(subtotal: number): number {
  // Simplified tax calculation - 8.5% average
  return Math.round(subtotal * 0.085)
}

function calculateShipping(items: CartItem[]): number {
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  
  // Free shipping over $75
  if (subtotal >= 7500) return 0
  
  // Base shipping $5.99
  const baseShipping = 599
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0)
  
  // $2 per additional item
  const additionalCost = Math.max(0, (itemCount - 1) * 200)
  
  return baseShipping + additionalCost
}

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, {
    items: [],
    isLoading: false,
  })

  // Load cart from localStorage on mount
  useEffect(() => {
    try {
      const savedCart = localStorage.getItem('cart')
      if (savedCart) {
        const items = JSON.parse(savedCart)
        dispatch({ type: 'LOAD_CART', payload: items })
      }
    } catch (error) {
      console.error('Error loading cart from localStorage:', error)
    }
  }, [])

  // Save cart to localStorage whenever items change
  useEffect(() => {
    try {
      localStorage.setItem('cart', JSON.stringify(state.items))
    } catch (error) {
      console.error('Error saving cart to localStorage:', error)
    }
  }, [state.items])

  const addItem = (item: CartItem) => {
    dispatch({ type: 'ADD_ITEM', payload: item })
  }

  const removeItem = (id: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: id })
  }

  const updateQuantity = (id: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { id, quantity } })
  }

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' })
  }

  // Calculate totals
  const subtotal = state.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  const tax = calculateTax(subtotal)
  const shipping = calculateShipping(state.items)
  const total = subtotal + tax + shipping
  const itemCount = state.items.reduce((sum, item) => sum + item.quantity, 0)

  const value: CartContextType = {
    items: state.items,
    subtotal,
    tax,
    shipping,
    total,
    itemCount,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    isLoading: state.isLoading,
  }

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const context = useContext(CartContext)
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
}