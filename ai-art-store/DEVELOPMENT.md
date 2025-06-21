# Development Guide - The Visible Words AI Art Store

## 🛠️ Development Environment Setup

### Prerequisites
- Node.js 18+ 
- PostgreSQL 14+
- Git
- VS Code (recommended)

### Quick Start
```bash
# Clone the repository
git clone [repository-url]
cd ai-art-store

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Set up database
npx prisma generate
npx prisma db push

# Start development server
npm run dev
```

## 📋 What's Already Built

### ✅ Core Infrastructure
- **Next.js 15** application with App Router
- **TypeScript** configuration and type definitions
- **Tailwind CSS** styling system
- **Prisma ORM** with complete database schema
- **ESLint & Prettier** code formatting

### ✅ E-Commerce Foundation
- **Shopping Cart** with persistent storage
- **Product Display** components and layouts
- **Checkout Flow** with form validation
- **Order Management** system architecture

### ✅ Payment Integration
- **Stripe Checkout** complete implementation
- **Webhook Handlers** for payment processing
- **Order Fulfillment** automation
- **Success/Cancel** pages

### ✅ Printify Integration (PHASE 1 COMPLETE)
- **Complete API Layer** with products, categories, search, filtering
- **Printify Sync System** - Real product sync from Printify
- **Admin Sync Tools** - Manual and automated sync capabilities
- **Product Management** - Full CRUD operations
- **Database Seeding** - Sample data with realistic products
- **Category Mapping** - Printify blueprints to product categories
- **Live Data Integration** - Fresh pricing and variant data

### ✅ User Interface
- **Responsive Design** for all screen sizes
- **Component Library** with consistent styling
- **Navigation System** with mobile support
- **Loading States** and error handling

## 🚧 What Still Needs to Be Built

### 🔴 Current Phase: Shop Display System

#### 1. Shop Listing Pages (PHASE 2 - IN PROGRESS)
**Priority: HIGH**
- **Shop Page** (`/shop`) with product grid display
- **Product Detail Pages** (`/product/[id]`) with variants
- **Search and Filtering** UI components
- **Category Navigation** and breadcrumbs

**Estimated Time: 1-2 days**

### 🟡 Upcoming Phases

#### 2. Admin Dashboard (PHASE 3)
**Priority: HIGH**
- **Admin Dashboard** for managing products and orders
- **Printify Integration UI** for product sync
- **Analytics and Reporting** interface
- **Order Management** tools

**Estimated Time: 2-3 days**

#### 3. User Account System (PHASE 4)
**Priority: MEDIUM**
- **User Registration/Login** with NextAuth.js
- **Order History** and account management
- **Profile Management** for customers
- **Password Reset** functionality

**Estimated Time: 1-2 days**

#### 4. Content & Polish (PHASE 5)
**Priority: MEDIUM**
- **Content Pages** (About, Contact, FAQ, Legal)
- **Custom Request System** for AI artwork
- **SEO Optimization** and meta tags
- **Performance Optimization** and caching

**Estimated Time: 2-3 days**

### 🔧 Technical Improvements Needed

#### 1. Data Population (✅ COMPLETED)
- ✅ **Sample Products** with realistic data
- ✅ **Database Seeding** scripts (`npm run db:seed`)
- ✅ **Product Categories** from Printify blueprints
- 🔲 **Image Assets** - Need actual product images

#### 2. Testing Infrastructure
- **Unit Tests** for components and utilities
- **Integration Tests** for API routes
- **E2E Tests** for critical user flows
- **Performance Testing** setup

#### 3. Development Tools
- **Storybook** for component development
- **API Documentation** with OpenAPI
- **Development Scripts** for common tasks
- **CI/CD Pipeline** configuration

## 🎯 Immediate Development Priorities

### Phase 1: Core Product System (Week 1)
1. **Create Shop Pages**
   ```bash
   # Files to create:
   app/shop/page.tsx              # Product listing
   app/shop/[category]/page.tsx   # Category pages
   app/product/[id]/page.tsx      # Product detail
   ```

2. **Add Product Management**
   ```bash
   # Files to create:
   app/admin/page.tsx             # Admin dashboard
   app/admin/products/page.tsx    # Product management
   app/api/products/route.ts      # Product API
   ```

3. **Implement Search & Filtering**
   ```bash
   # Files to create:
   components/shop/product-grid.tsx
   components/shop/filters.tsx
   components/shop/search.tsx
   ```

### Phase 2: User System (Week 2)
1. **Set up Authentication**
   ```bash
   npm install next-auth
   # Configure providers and callbacks
   ```

2. **Create Account Pages**
   ```bash
   app/account/page.tsx           # Account dashboard
   app/account/orders/page.tsx    # Order history
   app/login/page.tsx             # Login form
   ```

### Phase 3: Content & Polish (Week 3)
1. **Create Content Pages**
2. **Add Custom Request System** 
3. **Implement Testing**
4. **Performance Optimization**

## 🔍 Development Guidelines

### Code Organization
```
components/
  ├── ui/           # Reusable UI components
  ├── layout/       # Layout components
  ├── sections/     # Page sections
  ├── forms/        # Form components
  └── [feature]/    # Feature-specific components

lib/
  ├── api/          # API utilities
  ├── auth/         # Authentication logic
  ├── utils/        # Helper functions
  └── validations/  # Schema validations

app/
  ├── (auth)/       # Auth route group
  ├── admin/        # Admin pages
  ├── api/          # API routes
  └── [feature]/    # Feature pages
```

### Component Standards
```typescript
// Use this pattern for new components
interface ComponentProps {
  // Define props with JSDoc comments
}

export function ComponentName({ }: ComponentProps) {
  // Hooks at the top
  // Event handlers
  // Render logic
  
  return (
    <div className="semantic-classes">
      {/* Semantic HTML structure */}
    </div>
  )
}
```

### API Route Standards
```typescript
// Use this pattern for API routes
export async function GET(request: NextRequest) {
  try {
    // Validate request
    // Process data
    // Return response
    return NextResponse.json({ data })
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

## 🧪 Testing Strategy

### Unit Testing
```bash
# Install testing dependencies
npm install -D jest @testing-library/react @testing-library/jest-dom

# Test files should be co-located
components/
  ├── button.tsx
  ├── button.test.tsx
  └── button.stories.tsx
```

### Integration Testing
```bash
# API route testing
__tests__/
  ├── api/
  │   ├── products.test.ts
  │   └── checkout.test.ts
  └── pages/
      ├── shop.test.tsx
      └── checkout.test.tsx
```

### E2E Testing
```bash
# Install Playwright (already in dependencies)
npx playwright install

# Create test files
e2e/
  ├── checkout-flow.spec.ts
  ├── product-browsing.spec.ts
  └── admin-workflow.spec.ts
```

## 📊 Performance Considerations

### Image Optimization
- Use Next.js `Image` component
- Implement lazy loading
- Optimize for different screen sizes
- Consider using a CDN

### Database Optimization
- Add proper indexes to frequently queried columns
- Use database connection pooling
- Implement caching for static data
- Monitor query performance

### Bundle Optimization
- Code splitting for large features
- Dynamic imports for heavy components
- Tree shaking for unused code
- Bundle analyzer for optimization

## 🔐 Security Checklist

### Authentication & Authorization
- [ ] Secure session management
- [ ] Role-based access control
- [ ] API route protection
- [ ] Input validation and sanitization

### Data Protection
- [ ] Environment variable security
- [ ] Database connection encryption
- [ ] Payment data handling compliance
- [ ] User data privacy compliance

### Application Security
- [ ] HTTPS enforcement
- [ ] CSRF protection
- [ ] Rate limiting implementation
- [ ] Security headers configuration

## 🚀 Deployment Preparation

### Environment Configuration
```bash
# Development
NODE_ENV=development
NEXT_PUBLIC_BASE_URL=http://localhost:3000

# Production
NODE_ENV=production
NEXT_PUBLIC_BASE_URL=https://www.thevisiblewords.com
```

### Build Optimization
```bash
# Optimize for production
npm run build
npm run start

# Analyze bundle
npm run analyze
```

### Pre-deployment Checklist
- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] API endpoints tested
- [ ] Payment flow verified
- [ ] Error monitoring configured

## 📚 Resources & Documentation

### Framework Documentation
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Integration Guides
- [Stripe Integration Guide](https://stripe.com/docs/payments/checkout)
- [Printify API Documentation](https://developers.printify.com/)
- [NextAuth.js Documentation](https://next-auth.js.org/)

### Best Practices
- [React Best Practices](https://react.dev/learn)
- [TypeScript Best Practices](https://typescript-eslint.io/rules/)
- [Database Design Patterns](https://www.prisma.io/docs/guides/database)

---

## 🆘 Common Development Issues

### Build Errors
```bash
# Clear cache and reinstall
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

### Database Issues
```bash
# Reset database
npx prisma db push --force-reset
npx prisma generate
```

### Environment Variables
```bash
# Verify environment loading
console.log(process.env.NODE_ENV)
console.log(process.env.NEXT_PUBLIC_BASE_URL)
```

---

**Ready to continue development!** The foundation is solid - now we need to build the user-facing features and admin tools.