#!/bin/bash

# The Visible Words - AI Art Store Setup Script
# Sets up the Next.js e-commerce store

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo -e "${BLUE}"
    echo "🏪 ====================================================="
    echo "   The Visible Words - AI Art Store Setup"
    echo "   Next.js E-commerce Platform Configuration"
    echo "====================================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        echo "Please install Node.js 18+ from https://nodejs.org"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -c2-3)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    print_success "npm found: $(npm --version)"
    
    # Check if we're in the right directory
    if [[ ! -d "ai-art-store" ]]; then
        print_error "ai-art-store directory not found. Please run from project root."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Node.js dependencies..."
    
    cd ai-art-store
    
    # Clean install
    if [[ -d "node_modules" ]]; then
        print_status "Cleaning existing node_modules..."
        rm -rf node_modules package-lock.json
    fi
    
    npm install
    print_success "Dependencies installed successfully"
    
    cd ..
}

# Setup environment
setup_environment() {
    print_status "Setting up environment configuration..."
    
    cd ai-art-store
    
    # Create .env from .env.example if it doesn't exist
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env with your actual API keys:"
            print_warning "  - STRIPE_SECRET_KEY"
            print_warning "  - STRIPE_PUBLISHABLE_KEY" 
            print_warning "  - PRINTIFY_API_KEY"
            print_warning "  - PRINTIFY_SHOP_ID"
        else
            print_error ".env.example template not found"
            exit 1
        fi
    else
        print_success "Environment file already exists"
    fi
    
    cd ..
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    cd ai-art-store
    
    # Generate Prisma client
    print_status "Generating Prisma client..."
    npx prisma generate
    print_success "Prisma client generated"
    
    # Run database migrations
    print_status "Running database migrations..."
    npx prisma migrate dev --name init
    print_success "Database migrations completed"
    
    # Seed database with sample data
    print_status "Seeding database with sample data..."
    npx prisma db seed
    print_success "Database seeded successfully"
    
    print_success "Database setup complete"
    print_warning "Database file created at: prisma/dev.db"
    
    cd ..
}

# Check configuration
check_config() {
    print_status "Checking configuration..."
    
    cd ai-art-store
    
    # Check if .env has been configured
    if grep -q "YOUR_STRIPE_SECRET_KEY_HERE" .env 2>/dev/null; then
        print_warning "Stripe keys not configured in .env"
        print_warning "Add your keys from https://dashboard.stripe.com/apikeys"
    fi
    
    if grep -q "YOUR_PRINTIFY_API_TOKEN_HERE" .env 2>/dev/null; then
        print_warning "Printify credentials not configured in .env"
        print_warning "Add your credentials from https://printify.com/app/account/api"
    fi
    
    # Check if database exists
    if [[ -f "prisma/dev.db" ]]; then
        print_success "Database file exists"
    else
        print_warning "Database file not found - run database setup"
    fi
    
    cd ..
}

# Test application startup
test_startup() {
    print_status "Testing application startup..."
    
    cd ai-art-store
    
    # Build application to check for errors
    print_status "Building application..."
    if npm run build; then
        print_success "Application builds successfully"
    else
        print_error "Build failed - check for missing dependencies or configuration"
        exit 1
    fi
    
    cd ..
}

# Launch development server
launch_dev() {
    print_status "Launching development server..."
    
    cd ai-art-store
    
    print_success "Starting The Visible Words AI Art Store..."
    echo ""
    echo -e "${GREEN}🌐 Store will be available at: http://localhost:3000${NC}"
    echo -e "${YELLOW}📄 Shop page: http://localhost:3000/shop${NC}"
    echo -e "${YELLOW}🛒 Sample products available after seeding${NC}"
    echo ""
    echo -e "${BLUE}Press Ctrl+C to stop the development server${NC}"
    echo ""
    
    npm run dev
}

# Display next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Configure your API keys in ai-art-store/.env"
    echo "2. Start the development server:"
    echo "   cd ai-art-store && npm run dev"
    echo "3. Visit http://localhost:3000 to see your store"
    echo ""
    echo -e "${BLUE}API Keys needed:${NC}"
    echo "• Stripe: https://dashboard.stripe.com/apikeys"
    echo "• Printify: https://printify.com/app/account/api"
    echo ""
    echo -e "${BLUE}Store features:${NC}"
    echo "• Product catalog with search and filtering"
    echo "• Shopping cart with Stripe checkout"
    echo "• Admin tools for Printify integration"
    echo "• Mobile-responsive design"
}

# Display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev        Launch development server after setup"
    echo "  --test       Test build without launching"
    echo "  --help       Show this help message"
    echo ""
    echo "Default: Setup only, no launch"
}

# Main execution
main() {
    print_banner
    
    # Parse command line arguments
    LAUNCH_DEV=false
    TEST_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                LAUNCH_DEV=true
                shift
                ;;
            --test)
                TEST_ONLY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_prerequisites
    install_dependencies
    setup_environment
    setup_database
    check_config
    
    if [[ "$TEST_ONLY" == true ]]; then
        test_startup
        print_success "Test completed successfully"
    elif [[ "$LAUNCH_DEV" == true ]]; then
        test_startup
        launch_dev
    else
        show_next_steps
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}🛑 Shutting down...${NC}"; exit 0' SIGINT

# Run main function
main "$@"