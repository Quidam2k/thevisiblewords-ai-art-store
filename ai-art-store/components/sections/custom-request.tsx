import Link from 'next/link'

export function CustomRequestSection() {
  return (
    <section className="py-16 bg-gradient-to-br from-purple-900 to-blue-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl font-bold mb-6">
              Have Something Specific in Mind?
            </h2>
            <p className="text-xl text-purple-100 mb-8">
              Our AI can create custom artwork based on your ideas, descriptions, 
              or inspiration. From personal portraits to business logos, 
              we bring your vision to life.
            </p>
            
            <div className="space-y-4 mb-8">
              <div className="flex items-center">
                <svg className="w-6 h-6 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Custom artwork from your ideas</span>
              </div>
              <div className="flex items-center">
                <svg className="w-6 h-6 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Professional quality prints</span>
              </div>
              <div className="flex items-center">
                <svg className="w-6 h-6 text-green-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Fast turnaround time</span>
              </div>
            </div>

            <Link
              href="/custom"
              className="inline-flex items-center bg-white text-purple-900 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-purple-50 transition-colors"
            >
              Start Custom Request
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>

          <div className="relative">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8">
              <h3 className="text-2xl font-bold mb-6">How It Works</h3>
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-4">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">Describe Your Vision</h4>
                    <p className="text-purple-100 text-sm">Tell us what you want in detail</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-4">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">AI Creates Your Art</h4>
                    <p className="text-purple-100 text-sm">Our AI generates unique artwork</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-4">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">Review & Order</h4>
                    <p className="text-purple-100 text-sm">Approve the design and place your order</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}