// Core Types for AI Art Store
// These types define the data structures used throughout the application

import { type Prisma } from '@prisma/client'

// ===================================
// ARTWORK & IMAGE TYPES
// ===================================

export interface ImageAnalysis {
  dimensions: {
    width: number
    height: number
    aspectRatio: number
  }
  hasAlpha: boolean
  dominantColors: string[]
  complexity: 'low' | 'medium' | 'high'
  recommendedProducts: ProductRecommendation[]
  fileSize: number
  quality: 'low' | 'medium' | 'high'
}

export interface ProductRecommendation {
  printifyBlueprintId: number
  confidence: number
  reason: string
  variants: number[]
  category: string
  name: string
}

// ===================================
// PRODUCT TYPES
// ===================================

export interface ProductVariant {
  id: number
  price: number
  title: string
  options: {
    size?: string
    color?: string
    [key: string]: string | undefined
  }
  available: boolean
  inventory?: number
}

export interface PrintArea {
  variantIds: number[]
  placeholders: {
    position: string
    height: number
    width: number
  }[]
}

// Enhanced Product type with relations
export type ProductWithArtwork = Prisma.ProductGetPayload<{
  include: {
    artwork: true
  }
}>

export type ArtworkWithProducts = Prisma.ArtworkGetPayload<{
  include: {
    products: true
  }
}>

// ===================================
// CART & CHECKOUT TYPES
// ===================================

export interface CartItem {
  id: string
  productId: string
  title: string
  price: number
  quantity: number
  variant: {
    id: number
    title: string
    options: Record<string, string>
  }
  image: string
  artworkStyle: 'WHIMSY' | 'EPIC' | 'HYBRID'
}

export interface Cart {
  items: CartItem[]
  subtotal: number
  tax: number
  shipping: number
  total: number
  itemCount: number
}

export interface ShippingAddress {
  firstName: string
  lastName: string
  company?: string
  address1: string
  address2?: string
  city: string
  state: string
  country: string
  zip: string
}

export interface CheckoutData {
  customerEmail: string
  customerName: string
  customerPhone?: string
  shippingAddress: ShippingAddress
  billingAddress?: ShippingAddress
  cartItems: CartItem[]
  paymentMethodId?: string
}

// ===================================
// STRIPE TYPES
// ===================================

export interface StripeCheckoutSession {
  sessionId: string
  paymentIntentId: string
  amount: number
  currency: string
  customerEmail: string
  metadata: Record<string, string>
}

export interface StripeWebhookEvent {
  id: string
  type: string
  data: {
    object: any
  }
  created: number
}

// ===================================
// PRINTIFY TYPES
// ===================================

export interface PrintifyProduct {
  id: string
  title: string
  description: string
  blueprint_id: number
  print_provider_id: number
  variants: PrintifyVariant[]
  images: PrintifyImage[]
  created_at: string
  updated_at: string
  visible: boolean
  is_locked: boolean
  tags: string[]
}

export interface PrintifyVariant {
  id: number
  price: number
  title: string
  options: Record<string, any>
  placeholders: any[]
}

export interface PrintifyImage {
  src: string
  variant_ids: number[]
  position: string
  is_default: boolean
}

export interface PrintifyOrderRequest {
  external_id: string
  line_items: {
    product_id: string
    variant_id: number
    quantity: number
  }[]
  shipping_method: number
  send_shipping_notification: boolean
  address_to: {
    first_name: string
    last_name: string
    email: string
    phone: string
    country: string
    region: string
    address1: string
    address2?: string
    city: string
    zip: string
  }
}

// ===================================
// API RESPONSE TYPES
// ===================================

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T = any> {
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
}

// ===================================
// ADMIN TYPES
// ===================================

export interface BulkUploadJob {
  id: string
  artworks: File[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  results: ArtworkUploadResult[]
  startedAt: Date
  completedAt?: Date
}

export interface ArtworkUploadResult {
  filename: string
  artwork?: ArtworkWithProducts
  products?: ProductWithArtwork[]
  status: 'success' | 'failed'
  error?: string
  warnings?: string[]
}

export interface AdminStats {
  totalArtworks: number
  totalProducts: number
  totalOrders: number
  totalRevenue: number
  recentOrders: number
  conversionRate: number
  topProducts: {
    id: string
    title: string
    sales: number
    revenue: number
  }[]
  salesOverTime: {
    date: string
    orders: number
    revenue: number
  }[]
}

// ===================================
// SEARCH & FILTER TYPES
// ===================================

export interface ProductFilters {
  style?: 'WHIMSY' | 'EPIC' | 'HYBRID' | 'all'
  category?: string
  priceRange?: {
    min: number
    max: number
  }
  sortBy?: 'newest' | 'price-low' | 'price-high' | 'popular'
  search?: string
  tags?: string[]
  page?: number
  limit?: number
}

export interface SearchResult<T = any> {
  results: T[]
  total: number
  query: string
  filters: ProductFilters
  suggestions?: string[]
}

// ===================================
// UTILITY TYPES
// ===================================

export type AsyncReturnType<T extends (...args: any) => Promise<any>> = T extends (
  ...args: any
) => Promise<infer R>
  ? R
  : any

export type OptionalExceptFor<T, TRequired extends keyof T> = Partial<T> &
  Pick<T, TRequired>

export type CreateType<T> = Omit<T, 'id' | 'createdAt' | 'updatedAt'>

export type UpdateType<T> = Partial<Omit<T, 'id' | 'createdAt' | 'updatedAt'>>

// ===================================
// FORM TYPES
// ===================================

export interface ContactForm {
  name: string
  email: string
  subject: string
  message: string
}

export interface CustomRequestForm {
  customerName: string
  customerEmail: string
  prompt: string
  preferredProducts: string[]
  budget?: number
  timeline?: string
  additionalDetails?: string
}

export interface NewsletterSignup {
  email: string
  name?: string
  source?: string
}

// ===================================
// ERROR TYPES
// ===================================

export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: Date
  userId?: string
}

export interface ValidationError {
  field: string
  message: string
  value?: any
}

// ===================================
// ANALYTICS TYPES
// ===================================

export interface AnalyticsEvent {
  type: 'page_view' | 'product_view' | 'add_to_cart' | 'purchase' | 'custom_request'
  data: Record<string, any>
  userId?: string
  productId?: string
  value?: number
}

export interface ConversionFunnel {
  step: string
  visitors: number
  conversions: number
  conversionRate: number
}

// ===================================
// FEATURE FLAGS
// ===================================

export interface FeatureFlags {
  enableCustomRequests: boolean
  enableBulkUpload: boolean
  enableAnalytics: boolean
  enableNewsletter: boolean
  enableChatSupport: boolean
  enableSocialLogin: boolean
  maintenanceMode: boolean
}

export default {}