import Link from 'next/link'

export function StyleShowcase() {
  const styles = [
    {
      name: 'Whimsy',
      description: 'Playful, colorful, and imaginative designs that spark joy and wonder.',
      color: 'from-blue-400 to-cyan-400',
      href: '/shop?style=whimsy',
      features: ['Bright Colors', 'Playful Themes', 'Cheerful Vibes']
    },
    {
      name: 'Epic',
      description: 'Bold, dramatic artwork with powerful themes and striking visuals.',
      color: 'from-red-500 to-orange-500',
      href: '/shop?style=epic',
      features: ['Bold Designs', 'Dramatic Scenes', 'Powerful Impact']
    },
    {
      name: 'Hybrid',
      description: 'The perfect blend of whimsical charm and epic grandeur.',
      color: 'from-purple-500 to-pink-500',
      href: '/shop?style=hybrid',
      features: ['Best of Both', 'Unique Blend', 'Versatile Style']
    }
  ]

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Our Art Philosophy
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Three distinct approaches to AI-generated art, each crafted through 
            iterative prompting and careful curation to bring text to visual life.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {styles.map((style) => (
            <div
              key={style.name}
              className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300"
            >
              <div className={`h-32 bg-gradient-to-br ${style.color}`}>
                <div className="h-full flex items-center justify-center">
                  <h3 className="text-2xl font-bold text-white">{style.name}</h3>
                </div>
              </div>
              
              <div className="p-6">
                <p className="text-gray-600 mb-4">{style.description}</p>
                
                <ul className="space-y-2 mb-6">
                  {style.features.map((feature) => (
                    <li key={feature} className="flex items-center text-sm text-gray-700">
                      <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <Link
                  href={style.href}
                  className={`block w-full text-center bg-gradient-to-r ${style.color} text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200`}
                >
                  Explore {style.name}
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}