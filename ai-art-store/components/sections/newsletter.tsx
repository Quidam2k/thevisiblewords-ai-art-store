import { NewsletterSignup } from '@/components/forms/newsletter-signup'

export function Newsletter() {
  return (
    <section className="py-16 bg-gradient-to-r from-purple-600 to-pink-600">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">
          Stay in the Loop
        </h2>
        <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
          Get notified about new artwork, exclusive designs, and special offers. 
          Join our community of art lovers!
        </p>
        
        <NewsletterSignup />
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8 text-purple-100">
          <div>
            <div className="text-2xl font-bold text-white mb-2">500+</div>
            <div className="text-sm">Happy Customers</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white mb-2">1000+</div>
            <div className="text-sm">Unique Designs</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white mb-2">98%</div>
            <div className="text-sm">Satisfaction Rate</div>
          </div>
        </div>
      </div>
    </section>
  )
}