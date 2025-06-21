#!/bin/bash

# The Visible Words - Quick Start Script
# Automated setup and launch for the AI Art Automation Platform

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
    echo "🎨 ====================================================="
    echo "   The Visible Words - AI Art Automation Platform"
    echo "   Quick Start & Launch Script"
    echo "====================================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
    
    # Check if we're in the right directory
    if [[ ! -f "scripts/quickstart.sh" ]]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check if automation directory exists
    if [[ ! -d "printify-automation" ]]; then
        print_error "Printify automation directory not found"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    cd printify-automation
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    cd ..
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    cd printify-automation
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "../requirements.txt" ]]; then
        pip install -r ../requirements.txt
        print_success "Main dependencies installed"
    fi
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "Automation-specific dependencies installed"
    fi
    
    cd ..
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    cd printify-automation
    
    # Create config directory if it doesn't exist
    mkdir -p config
    
    # Copy config template if config doesn't exist
    if [[ ! -f "config/config.json" ]] && [[ -f "config/config.template.json" ]]; then
        cp config/config.template.json config/config.json
        print_success "Configuration template copied"
        print_warning "Please edit config/config.json with your Printify API credentials"
    elif [[ -f "config/config.json" ]]; then
        print_success "Configuration file already exists"
    else
        print_warning "No configuration template found"
    fi
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << 'EOF'
# The Visible Words - Environment Configuration
DATABASE_URL=sqlite:///./printify_automation.db
REDIS_URL=redis://localhost:6379
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=true
EOF
        print_success "Environment file created"
        print_warning "Please edit .env with your actual values"
    else
        print_success "Environment file already exists"
    fi
    
    cd ..
}

# Install Node.js dependencies
setup_nodejs() {
    print_status "Setting up Node.js dependencies..."
    
    cd printify-automation
    
    if [[ -f "package.json" ]] && command -v npm &> /dev/null; then
        npm install
        print_success "Node.js dependencies installed"
    elif [[ ! -f "package.json" ]]; then
        print_warning "No package.json found, skipping Node.js setup"
    else
        print_warning "npm not found, skipping Node.js dependencies"
        print_warning "Install Node.js for browser testing features"
    fi
    
    cd ..
}

# Run tests
run_tests() {
    print_status "Running initial tests..."
    
    cd printify-automation
    source venv/bin/activate
    
    if [[ -f "tests/run_tests.py" ]]; then
        python tests/run_tests.py
        print_success "Tests completed"
    else
        print_warning "Test runner not found, skipping tests"
    fi
    
    cd ..
}

# Launch application
launch_app() {
    print_status "Launching application..."
    
    cd printify-automation
    source venv/bin/activate
    
    if [[ -f "app.py" ]]; then
        print_success "Starting The Visible Words AI Art Automation Platform..."
        echo ""
        echo -e "${GREEN}🌐 Access the web interface at: http://localhost:7860${NC}"
        echo -e "${YELLOW}📚 Documentation available at: docs/${NC}"
        echo -e "${YELLOW}⚙️  Configuration file: config/config.json${NC}"
        echo ""
        echo -e "${BLUE}Press Ctrl+C to stop the application${NC}"
        echo ""
        
        python app.py
    else
        print_error "app.py not found"
        exit 1
    fi
}

# Docker deployment option
launch_docker() {
    print_status "Launching with Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is required but not installed"
        exit 1
    fi
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "Docker services started"
    echo ""
    echo -e "${GREEN}🌐 Access the web interface at: http://localhost${NC}"
    echo -e "${YELLOW}📊 Monitoring dashboard: http://localhost:3000${NC}"
    echo -e "${YELLOW}🗄️  Database admin: http://localhost:5050${NC}"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop services: docker-compose down"
}

# Display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker     Launch using Docker containers"
    echo "  --dev        Install development dependencies"
    echo "  --test-only  Only run tests, don't launch app"
    echo "  --help       Show this help message"
    echo ""
    echo "Default: Launch with Python virtual environment"
}

# Main execution
main() {
    print_banner
    
    # Parse command line arguments
    DOCKER_MODE=false
    DEV_MODE=false
    TEST_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                DOCKER_MODE=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            --test-only)
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
    
    check_prerequisites
    
    if [[ "$DOCKER_MODE" == true ]]; then
        launch_docker
    else
        setup_venv
        install_dependencies
        setup_config
        setup_nodejs
        
        if [[ "$TEST_ONLY" == true ]]; then
            run_tests
        else
            run_tests
            launch_app
        fi
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}🛑 Shutting down...${NC}"; exit 0' SIGINT

# Run main function
main "$@"