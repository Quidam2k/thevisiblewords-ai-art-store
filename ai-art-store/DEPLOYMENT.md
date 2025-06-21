# Deployment Guide - The Visible Words AI Art Store

## 🚀 Production Deployment Checklist

### Pre-Deployment Requirements

#### 1. Environment Setup
```env
# Database Configuration
DATABASE_URL="postgresql://username:password@host:port/database"
DIRECT_URL="postgresql://username:password@host:port/database"

# Stripe Configuration
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_PUBLISHABLE_KEY="pk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Printify Configuration
PRINTIFY_API_KEY="your_live_printify_api_key"
PRINTIFY_SHOP_ID="your_printify_shop_id"

# Application Configuration
NEXT_PUBLIC_BASE_URL="https://www.thevisiblewords.com"
NODE_ENV="production"
```

#### 2. Database Setup
```bash
# Run database migrations
npx prisma db push

# Generate Prisma client
npx prisma generate

# (Optional) Seed initial data
npx prisma db seed
```

#### 3. Stripe Configuration
1. **Create Production Webhook Endpoint**
   - URL: `https://www.thevisiblewords.com/api/webhooks/stripe`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`

2. **Test Webhook Connection**
   ```bash
   stripe listen --forward-to localhost:3000/api/webhooks/stripe
   ```

#### 4. Domain & SSL
- Configure DNS to point to your hosting provider
- Ensure SSL certificate is properly installed
- Test HTTPS redirects work correctly

### Deployment Options

#### Option 1: Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to production
vercel --prod

# Configure environment variables in Vercel dashboard
# Set up database connection
# Configure custom domain
```

#### Option 2: Docker + Cloud Provider
```dockerfile
# Use the provided Dockerfile
docker build -t ai-art-store .
docker run -p 3000:3000 ai-art-store
```

#### Option 3: Traditional VPS
```bash
# Install Node.js 18+
# Install PostgreSQL
# Clone repository
# Install dependencies
npm install

# Build application
npm run build

# Start with PM2
npm install -g pm2
pm2 start npm --name "ai-art-store" -- start
```

### Post-Deployment Verification

#### 1. Core Functionality Tests
- [ ] Homepage loads correctly
- [ ] Product listings display (when products added)
- [ ] Cart functionality works
- [ ] Checkout process completes
- [ ] Payment processing works
- [ ] Order confirmation emails sent
- [ ] Webhook events process correctly

#### 2. Integration Tests
- [ ] Stripe webhooks receiving events
- [ ] Printify orders submit successfully
- [ ] Database connections stable
- [ ] Environment variables loaded
- [ ] SSL certificate valid

#### 3. Performance Checks
- [ ] Page load times < 3 seconds
- [ ] Images optimized and loading
- [ ] Database queries performing well
- [ ] CDN configured (if applicable)

### Monitoring & Maintenance

#### Error Monitoring
```javascript
// Consider integrating services like:
// - Sentry for error tracking
// - LogRocket for session replay
// - Vercel Analytics for performance
```

#### Database Monitoring
- Monitor connection pool usage
- Track query performance
- Set up automated backups
- Monitor disk space usage

#### Payment Monitoring
- Monitor Stripe webhook delivery
- Track failed payments
- Monitor chargeback rates
- Set up fraud detection alerts

### Security Considerations

#### Environment Variables
- Never commit `.env` files to version control
- Use secure environment variable management
- Rotate API keys regularly
- Use different keys for development/production

#### Database Security
- Use connection pooling
- Enable SSL connections
- Regular security updates
- Monitor for suspicious activity

#### Application Security
- Keep dependencies updated
- Use HTTPS everywhere
- Implement rate limiting
- Validate all user inputs

### Backup Strategy

#### Database Backups
```bash
# Daily automated backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Weekly full backups to cloud storage
# Monthly backup retention cleanup
```

#### Code Backups
- Use Git with multiple remotes
- Tag release versions
- Maintain staging environment
- Document rollback procedures

### Troubleshooting Common Issues

#### Deployment Failures
1. **Build Errors**
   - Check TypeScript compilation
   - Verify all dependencies installed
   - Check environment variables

2. **Database Connection Issues**
   - Verify connection string format
   - Check firewall rules
   - Test database connectivity

3. **Payment Processing Issues**
   - Verify Stripe webhook URL
   - Check webhook secret key
   - Monitor Stripe dashboard for errors

#### Performance Issues
1. **Slow Page Loads**
   - Enable compression
   - Optimize images
   - Implement caching
   - Use CDN for static assets

2. **Database Performance**
   - Analyze slow queries
   - Add database indexes
   - Consider connection pooling
   - Monitor query plans

### Scaling Considerations

#### Horizontal Scaling
- Use load balancer for multiple instances
- Implement session storage (Redis)
- Database read replicas
- CDN for static assets

#### Vertical Scaling
- Monitor resource usage
- Upgrade server specifications
- Optimize database performance
- Implement caching layers

### Migration from Shopify

#### Data Export
1. **Product Data**
   - Export product catalog
   - Download product images
   - Export customer data
   - Export order history

2. **SEO Preservation**
   - Map old URLs to new URLs
   - Implement 301 redirects
   - Update sitemap.xml
   - Submit to search engines

3. **Customer Communication**
   - Notify customers of migration
   - Provide new account setup instructions
   - Offer migration assistance
   - Update social media links

#### DNS Cutover
1. **Preparation**
   - Test new site thoroughly
   - Prepare rollback plan
   - Schedule during low traffic
   - Notify team of timeline

2. **Execution**
   - Update DNS records
   - Monitor traffic flow
   - Test critical functionality
   - Monitor error rates

3. **Post-Migration**
   - Monitor site performance
   - Address any issues quickly
   - Update marketing materials
   - Gather user feedback

### Support & Maintenance

#### Regular Maintenance Tasks
- [ ] Weekly dependency updates
- [ ] Monthly security patches
- [ ] Quarterly performance reviews
- [ ] Annual architecture reviews

#### Documentation Updates
- Keep deployment docs current
- Document configuration changes
- Maintain troubleshooting guides
- Update team contact information

---

## 🆘 Emergency Procedures

### Rollback Plan
1. Revert DNS changes
2. Restore previous deployment
3. Notify customers of temporary issues
4. Investigate and fix problems
5. Plan re-deployment

### Contact Information
- **Technical Lead**: [Your Contact]
- **DevOps Support**: [DevOps Contact]
- **Emergency Escalation**: [Emergency Contact]

---

**Remember**: Always test deployments in a staging environment first!