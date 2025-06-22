// Printify API Client
import { PrintifyProduct, PrintifyOrderRequest, ApiResponse } from '@/types'

class PrintifyAPI {
  private baseURL = 'https://api.printify.com/v1'
  private apiKey: string
  private shopId: string

  constructor() {
    this.apiKey = process.env.PRINTIFY_API_KEY!
    this.shopId = process.env.PRINTIFY_SHOP_ID!
    
    if (!this.apiKey || !this.shopId) {
      throw new Error('Printify API credentials are required')
    }
  }

  private async request<T = any>(
    method: string,
    endpoint: string,
    data?: any
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method,
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : undefined,
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Printify API error: ${response.status} ${errorText}`)
      }

      const result = await response.json()
      return {
        success: true,
        data: result,
      }
    } catch (error) {
      console.error('Printify API error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }
    }
  }

  // Upload image to Printify
  async uploadImage(filename: string, imageData: string): Promise<ApiResponse> {
    return this.request('POST', '/uploads/images.json', {
      file_name: filename,
      contents: imageData,
    })
  }

  // Get available blueprints
  async getBlueprints(): Promise<ApiResponse> {
    return this.request('GET', '/catalog/blueprints.json')
  }

  // Get print providers for a blueprint
  async getPrintProviders(blueprintId: number): Promise<ApiResponse> {
    return this.request('GET', `/catalog/blueprints/${blueprintId}/print_providers.json`)
  }

  // Get variants for a blueprint and provider
  async getVariants(blueprintId: number, providerId: number): Promise<ApiResponse> {
    return this.request('GET', `/catalog/blueprints/${blueprintId}/print_providers/${providerId}/variants.json`)
  }

  // Create a product
  async createProduct(productData: any): Promise<ApiResponse<PrintifyProduct>> {
    return this.request('POST', `/shops/${this.shopId}/products.json`, productData)
  }

  // Get all products
  async getProducts(page = 1, limit = 50): Promise<ApiResponse> {
    return this.request('GET', `/shops/${this.shopId}/products.json?page=${page}&limit=${limit}`)
  }

  // Get single product
  async getProduct(productId: string): Promise<ApiResponse<PrintifyProduct>> {
    return this.request('GET', `/shops/${this.shopId}/products/${productId}.json`)
  }

  // Update product
  async updateProduct(productId: string, productData: any): Promise<ApiResponse> {
    return this.request('PUT', `/shops/${this.shopId}/products/${productId}.json`, productData)
  }

  // Delete product
  async deleteProduct(productId: string): Promise<ApiResponse> {
    return this.request('DELETE', `/shops/${this.shopId}/products/${productId}.json`)
  }

  // Submit order to Printify
  async submitOrder(orderData: PrintifyOrderRequest): Promise<ApiResponse> {
    return this.request('POST', `/shops/${this.shopId}/orders.json`, orderData)
  }

  // Get order status
  async getOrder(orderId: string): Promise<ApiResponse> {
    return this.request('GET', `/shops/${this.shopId}/orders/${orderId}.json`)
  }

  // Calculate shipping costs
  async calculateShipping(orderData: any): Promise<ApiResponse> {
    return this.request('POST', `/shops/${this.shopId}/orders/shipping.json`, orderData)
  }

  // Helper: Build product data for artwork
  buildProductData(artwork: {
    id: string
    title: string
    description?: string
    fileUrl: string
  }, blueprint: {
    id: number
    providerId: number
    variants: any[]
  }, imageId: string) {
    return {
      title: artwork.title,
      description: artwork.description || '',
      blueprint_id: blueprint.id,
      print_provider_id: blueprint.providerId,
      variants: blueprint.variants.map((variant: any) => ({
        id: variant.id,
        price: Math.round(variant.price * 2), // 100% markup
        is_enabled: true,
      })),
      print_areas: [{
        variant_ids: blueprint.variants.map((v: any) => v.id),
        placeholders: [{
          position: 'front',
          images: [{
            id: imageId,
            x: 0.5,
            y: 0.5,
            scale: 1,
            angle: 0,
          }],
        }],
      }],
    }
  }
}

export const printifyAPI = new PrintifyAPI()