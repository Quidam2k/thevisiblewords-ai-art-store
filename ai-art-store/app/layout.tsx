import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { CartProvider } from '@/components/providers/cart-provider'
import { Header } from '@/components/layout/header'
import { Footer } from '@/components/layout/footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'The Visible Words - AI Art & Print-on-Demand',
  description: 'Discover unique AI-generated art prints, custom designs, and premium quality merchandise. Transform your space with whimsical and epic art.',
  keywords: 'AI art, print on demand, custom art, wall art, t-shirts, mugs, posters',
  authors: [{ name: 'The Visible Words' }],
  openGraph: {
    title: 'The Visible Words - AI Art & Print-on-Demand',
    description: 'Discover unique AI-generated art prints and custom designs.',
    url: 'https://www.thevisiblewords.com',
    siteName: 'The Visible Words',
    type: 'website',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CartProvider>
          <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-1">
              {children}
            </main>
            <Footer />
          </div>
        </CartProvider>
      </body>
    </html>
  )
}