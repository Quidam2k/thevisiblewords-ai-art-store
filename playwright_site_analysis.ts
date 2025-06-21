// playwright-analysis.ts
// Run with: npx playwright test playwright-analysis.ts --headed

import { test, expect, Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';

interface ProductData {
  title: string;
  price: string;
  imageUrl: string;
  link: string;
  description?: string;
}

interface SiteAnalysis {
  homepage: {
    title: string;
    description: string;
    featuredProducts: ProductData[];
    navigation: string[];
    categories: string[];
  };
  products: ProductData[];
  siteStructure: {
    totalPages: number;
    productPages: string[];
    categories: string[];
  };
  design: {
    colorScheme: string[];
    fonts: string[];
    layout: string;
  };
  screenshots: string[];
}

test.describe('The Visible Words Site Analysis', () => {
  let siteAnalysis: SiteAnalysis;
  const screenshotDir = './site-analysis-screenshots';

  test.beforeAll(async () => {
    // Create screenshots directory
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    siteAnalysis = {
      homepage: {
        title: '',
        description: '',
        featuredProducts: [],
        navigation: [],
        categories: []
      },
      products: [],
      siteStructure: {
        totalPages: 0,
        productPages: [],
        categories: []
      },
      design: {
        colorScheme: [],
        fonts: [],
        layout: ''
      },
      screenshots: []
    };
  });

  test('Analyze homepage structure and design', async ({ page }) => {
    await page.goto('https://www.thevisiblewords.com');
    
    // Take homepage screenshot
    const homepageScreenshot = path.join(screenshotDir, 'homepage.png');
    await page.screenshot({ path: homepageScreenshot, fullPage: true });
    siteAnalysis.screenshots.push(homepageScreenshot);

    // Extract basic page info
    siteAnalysis.homepage.title = await page.title();
    
    // Look for meta description
    const metaDescription = await page.locator('meta[name="description"]').getAttribute('content');
    siteAnalysis.homepage.description = metaDescription || '';

    // Extract navigation
    const navLinks = await page.locator('nav a, header a').allTextContents();
    siteAnalysis.homepage.navigation = navLinks.filter(link => link.trim() !== '');

    // Extract featured products from homepage
    const productElements = await page.locator('[href*="/products/"]').all();
    
    for (const element of productElements.slice(0, 8)) { // Limit to first 8 products
      try {
        const link = await element.getAttribute('href') || '';
        const productContainer = element.locator('..'); // Get parent container
        
        // Try to extract product info from various possible structures
        const titleElement = await productContainer.locator('h1, h2, h3, h4, .product-title, [class*="title"]').first();
        const priceElement = await productContainer.locator('[class*="price"], .price, [data-price]').first();
        const imageElement = await productContainer.locator('img').first();
        
        const title = await titleElement.textContent() || '';
        const price = await priceElement.textContent() || '';
        const imageUrl = await imageElement.getAttribute('src') || '';
        
        if (title && link) {
          siteAnalysis.homepage.featuredProducts.push({
            title: title.trim(),
            price: price.trim(),
            imageUrl,
            link: link.startsWith('http') ? link : `https://www.thevisiblewords.com${link}`
          });
        }
      } catch (error) {
        console.log('Error extracting product:', error);
      }
    }

    // Extract categories/style sections
    const categoryElements = await page.locator('h1, h2, h3').allTextContents();
    const categories = categoryElements.filter(text => 
      ['whimsy', 'epic', 'hybrid', 'featured', 'collection'].some(keyword => 
        text.toLowerCase().includes(keyword)
      )
    );
    siteAnalysis.homepage.categories = categories;

    // Extract color scheme by analyzing CSS
    const primaryColors = await page.evaluate(() => {
      const styles = getComputedStyle(document.body);
      return {
        backgroundColor: styles.backgroundColor,
        color: styles.color,
        accentColor: styles.getPropertyValue('--accent-color') || 'not-set'
      };
    });
    
    siteAnalysis.design.colorScheme = Object.values(primaryColors);

    console.log('Homepage analysis complete:', {
      title: siteAnalysis.homepage.title,
      productsFound: siteAnalysis.homepage.featuredProducts.length,
      navigation: siteAnalysis.homepage.navigation,
      categories: siteAnalysis.homepage.categories
    });
  });

  test('Analyze individual product pages', async ({ page }) => {
    // Visit a few product pages to understand structure
    const productLinks = siteAnalysis.homepage.featuredProducts.slice(0, 3).map(p => p.link);
    
    for (let i = 0; i < productLinks.length; i++) {
      const productUrl = productLinks[i];
      
      try {
        await page.goto(productUrl);
        await page.waitForLoadState('networkidle');
        
        // Take screenshot
        const productScreenshot = path.join(screenshotDir, `product-${i + 1}.png`);
        await page.screenshot({ path: productScreenshot, fullPage: true });
        siteAnalysis.screenshots.push(productScreenshot);

        // Extract detailed product information
        const title = await page.locator('h1, .product-title, [class*="title"]').first().textContent();
        const price = await page.locator('.price, [class*="price"], [data-price]').first().textContent();
        const description = await page.locator('.product-description, [class*="description"], .rte').first().textContent();
        const images = await page.locator('.product-image img, .product-photos img').all();
        
        const productImages = [];
        for (const img of images) {
          const src = await img.getAttribute('src');
          if (src) productImages.push(src);
        }

        const productData: ProductData = {
          title: title?.trim() || '',
          price: price?.trim() || '',
          imageUrl: productImages[0] || '',
          link: productUrl,
          description: description?.trim() || ''
        };

        siteAnalysis.products.push(productData);
        siteAnalysis.siteStructure.productPages.push(productUrl);

        console.log(`Analyzed product ${i + 1}:`, productData.title);
        
        // Small delay to be respectful
        await page.waitForTimeout(1000);
        
      } catch (error) {
        console.log(`Error analyzing product ${productUrl}:`, error);
      }
    }
  });

  test('Analyze product collection/category pages', async ({ page }) => {
    // Try to find collection/category pages
    const potentialCategoryUrls = [
      'https://www.thevisiblewords.com/collections',
      'https://www.thevisiblewords.com/collections/all',
      'https://www.thevisiblewords.com/products',
      'https://www.thevisiblewords.com/shop'
    ];

    for (const url of potentialCategoryUrls) {
      try {
        const response = await page.goto(url);
        if (response?.ok()) {
          await page.waitForLoadState('networkidle');
          
          const categoryScreenshot = path.join(screenshotDir, `category-${url.split('/').pop()}.png`);
          await page.screenshot({ path: categoryScreenshot, fullPage: true });
          siteAnalysis.screenshots.push(categoryScreenshot);

          // Extract products from category page
          const categoryProducts = await page.locator('[href*="/products/"]').all();
          console.log(`Found ${categoryProducts.length} products on ${url}`);
          
          siteAnalysis.siteStructure.categories.push(url);
        }
      } catch (error) {
        console.log(`Category page ${url} not accessible:`, error);
      }
    }
  });

  test('Analyze site performance and technical details', async ({ page }) => {
    await page.goto('https://www.thevisiblewords.com');
    
    // Analyze page load performance
    const performanceEntries = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        loadTime: navigation.loadEventEnd - navigation.loadEventStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        totalPageLoad: navigation.loadEventEnd - navigation.fetchStart
      };
    });

    // Extract technical details
    const technicalDetails = await page.evaluate(() => {
      return {
        platform: document.querySelector('meta[name="generator"]')?.getAttribute('content') || 'unknown',
        viewport: document.querySelector('meta[name="viewport"]')?.getAttribute('content') || '',
        charset: document.characterSet,
        scripts: Array.from(document.scripts).map(script => script.src).filter(src => src),
        stylesheets: Array.from(document.styleSheets).map(sheet => sheet.href).filter(href => href)
      };
    });

    console.log('Performance metrics:', performanceEntries);
    console.log('Technical details:', technicalDetails);

    // Store in analysis
    siteAnalysis.design.layout = 'responsive'; // Default assumption
  });

  test.afterAll(async () => {
    // Save complete analysis to JSON file
    const analysisFile = path.join(screenshotDir, 'site-analysis.json');
    fs.writeFileSync(analysisFile, JSON.stringify(siteAnalysis, null, 2));
    
    // Create a summary report
    const summaryReport = `
# The Visible Words - Site Analysis Report

## Homepage Overview
- **Title**: ${siteAnalysis.homepage.title}
- **Description**: ${siteAnalysis.homepage.description}
- **Featured Products**: ${siteAnalysis.homepage.featuredProducts.length} products found
- **Navigation Items**: ${siteAnalysis.homepage.navigation.join(', ')}
- **Categories**: ${siteAnalysis.homepage.categories.join(', ')}

## Product Analysis
- **Total Products Analyzed**: ${siteAnalysis.products.length}
- **Product Categories**: ${siteAnalysis.siteStructure.categories.length} category pages found
- **Sample Products**:
${siteAnalysis.products.map(p => `  - ${p.title} (${p.price})`).join('\n')}

## Technical Details
- **Color Scheme**: ${siteAnalysis.design.colorScheme.join(', ')}
- **Layout**: ${siteAnalysis.design.layout}

## Migration Notes
1. **Product Data**: ${siteAnalysis.products.length} products need to be migrated
2. **Image Assets**: All product images need to be downloaded and re-uploaded
3. **Content**: Product descriptions and titles are available for migration
4. **Categories**: Site uses style-based categorization (Whimsy, Epic, Hybrid)
5. **Navigation**: Simple navigation structure suitable for custom implementation

## Recommendations for Custom Site
1. **Preserve**: Current categorization system (Whimsy/Epic/Hybrid)
2. **Improve**: Product discovery with better filtering and search
3. **Enhance**: Product pages with better image displays
4. **Add**: Bulk upload system for new AI artwork
5. **Optimize**: Performance and SEO improvements

## Screenshots Captured
${siteAnalysis.screenshots.map(path => `- ${path}`).join('\n')}
`;

    const reportFile = path.join(screenshotDir, 'analysis-report.md');
    fs.writeFileSync(reportFile, summaryReport);
    
    console.log('\n=== SITE ANALYSIS COMPLETE ===');
    console.log(`Screenshots saved to: ${screenshotDir}`);
    console.log(`Analysis data: ${analysisFile}`);
    console.log(`Summary report: ${reportFile}`);
    console.log('\nKey findings:');
    console.log(`- ${siteAnalysis.homepage.featuredProducts.length} featured products found`);
    console.log(`- ${siteAnalysis.products.length} detailed product pages analyzed`);
    console.log(`- ${siteAnalysis.siteStructure.categories.length} category pages found`);
    console.log(`- ${siteAnalysis.screenshots.length} screenshots captured`);
  });
});

// Additional utility test for extracting Shopify data
test('Extract Shopify-specific data for migration', async ({ page }) => {
  await page.goto('https://www.thevisiblewords.com');
  
  // Extract Shopify store data
  const shopifyData = await page.evaluate(() => {
    // Look for Shopify-specific variables
    const shopifyVars = (window as any).Shopify || {};
    const shopData = (window as any).shop || {};
    
    return {
      shop: shopData,
      shopify: shopifyVars,
      theme: document.querySelector('link[href*="theme"]')?.getAttribute('href') || '',
      apps: Array.from(document.scripts)
        .map(script => script.src)
        .filter(src => src && src.includes('shopify'))
    };
  });

  console.log('Shopify-specific data found:', shopifyData);
  
  // Save for migration planning
  const migrationData = {
    shopifyData,
    migrationTasks: [
      'Export product data via Shopify Admin API',
      'Download all product images',
      'Export customer data (if any)',
      'Export order history',
      'Set up redirects for SEO preservation',
      'Update DNS when ready to switch'
    ]
  };

  fs.writeFileSync('./site-analysis-screenshots/migration-plan.json', JSON.stringify(migrationData, null, 2));
});