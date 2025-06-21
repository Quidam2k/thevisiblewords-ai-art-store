import Link from 'next/link'
import Image from 'next/image'

export function Hero() {
  return (
    <section className="relative bg-gradient-to-br from-purple-100 to-pink-100 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Text Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Where AI Meets
                <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  {' '}Art
                </span>
              </h1>
              <p className="text-xl text-gray-600 max-w-lg">
                Discover unique AI-generated artwork transformed into premium quality 
                prints, apparel, and home decor. Every piece tells a story.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/shop"
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200 text-center"
              >
                Shop Now
              </Link>
              <Link
                href="/custom"
                className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:border-purple-600 hover:text-purple-600 transition-colors text-center"
              >
                Custom Request
              </Link>
            </div>

            {/* Features */}
            <div className="grid grid-cols-3 gap-4 pt-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">200+</div>
                <div className="text-sm text-gray-600">Unique Designs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">48hr</div>
                <div className="text-sm text-gray-600">Fast Shipping</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">100%</div>
                <div className="text-sm text-gray-600">Satisfaction</div>
              </div>
            </div>
          </div>

          {/* Image Showcase */}
          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="relative h-48 rounded-2xl overflow-hidden shadow-lg transform rotate-2 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-gradient-to-br from-blue-400 to-purple-600 w-full h-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">Whimsy Art</span>
                  </div>
                </div>
                <div className="relative h-32 rounded-2xl overflow-hidden shadow-lg transform -rotate-1 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-gradient-to-br from-green-400 to-blue-600 w-full h-full flex items-center justify-center">
                    <span className="text-white font-bold">Epic Style</span>
                  </div>
                </div>
              </div>
              <div className="space-y-4 pt-8">
                <div className="relative h-32 rounded-2xl overflow-hidden shadow-lg transform rotate-1 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-gradient-to-br from-pink-400 to-red-600 w-full h-full flex items-center justify-center">
                    <span className="text-white font-bold">Custom</span>
                  </div>
                </div>
                <div className="relative h-48 rounded-2xl overflow-hidden shadow-lg transform -rotate-2 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-gradient-to-br from-yellow-400 to-orange-600 w-full h-full flex items-center justify-center">
                    <span className="text-white font-bold text-lg">Hybrid Mix</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating elements */}
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-yellow-300 rounded-full opacity-60 animate-pulse"></div>
            <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-pink-300 rounded-full opacity-60 animate-pulse animation-delay-1000"></div>
          </div>
        </div>
      </div>

      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-purple-400 rounded-full opacity-40"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-pink-400 rounded-full opacity-60"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-blue-400 rounded-full opacity-30"></div>
      </div>
    </section>
  )
}