"""
Enhanced Printify API Client
Implements latest API features including V2 endpoints, advanced error handling,
and comprehensive rate limiting
"""

import requests
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
from datetime import datetime, timedelta

class APIVersion(Enum):
    V1 = "v1"
    V2 = "v2"

@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    remaining: int
    reset_time: datetime
    total_limit: int

@dataclass
class APIResponse:
    """Standardized API response"""
    success: bool
    data: Any
    status_code: int
    message: str
    rate_limit_info: Optional[RateLimitInfo] = None

class PrintifyAPIClient:
    def __init__(self, access_token: str, shop_id: str, config=None):
        self.access_token = access_token
        self.shop_id = shop_id
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.v1_base_url = "https://api.printify.com/v1"
        self.v2_base_url = "https://api.printify.com/v2"
        self.user_agent = config.get('user_agent', 'Printify-Automation-Tool') if config else 'Printify-Automation-Tool'
        
        # Rate limiting
        self.rate_limit_rpm = config.get('rate_limit_rpm', 600) if config else 600
        self.rate_limit_product_creation = config.get('rate_limit_product_creation', 200) if config else 200
        self.retry_attempts = config.get('retry_attempts', 3) if config else 3
        self.retry_delay = config.get('retry_delay', 1.0) if config else 1.0
        
        # Rate limiting state
        self._request_times = []
        self._product_creation_times = []
        self._lock = threading.Lock()
        
        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent
        })

    def _wait_for_rate_limit(self, is_product_creation: bool = False):
        """Enforce rate limiting"""
        with self._lock:
            now = time.time()
            
            if is_product_creation:
                # Product creation: 200 per 30 minutes
                cutoff_time = now - 1800  # 30 minutes
                self._product_creation_times = [t for t in self._product_creation_times if t > cutoff_time]
                
                if len(self._product_creation_times) >= self.rate_limit_product_creation:
                    sleep_time = self._product_creation_times[0] + 1800 - now
                    if sleep_time > 0:
                        self.logger.info(f"Rate limit: waiting {sleep_time:.1f}s for product creation")
                        time.sleep(sleep_time)
                        self._product_creation_times = []
                
                self._product_creation_times.append(now)
            
            # General rate limit: 600 per minute
            cutoff_time = now - 60  # 1 minute
            self._request_times = [t for t in self._request_times if t > cutoff_time]
            
            if len(self._request_times) >= self.rate_limit_rpm:
                sleep_time = self._request_times[0] + 60 - now
                if sleep_time > 0:
                    self.logger.info(f"Rate limit: waiting {sleep_time:.1f}s for general requests")
                    time.sleep(sleep_time)
                    self._request_times = []
            
            self._request_times.append(now)

    def _make_request(self, method: str, url: str, data: Any = None, 
                     is_product_creation: bool = False, api_version: APIVersion = APIVersion.V1) -> APIResponse:
        """Make an API request with comprehensive error handling and retry logic"""
        
        # Select base URL
        base_url = self.v2_base_url if api_version == APIVersion.V2 else self.v1_base_url
        full_url = f"{base_url}/{url.lstrip('/')}"
        
        for attempt in range(self.retry_attempts):
            try:
                # Rate limiting
                self._wait_for_rate_limit(is_product_creation)
                
                # Make request
                response = self.session.request(method, full_url, json=data)
                
                # Parse rate limit headers if available
                rate_limit_info = self._parse_rate_limit_headers(response.headers)
                
                # Handle different status codes
                if response.status_code == 200 or response.status_code == 201:
                    return APIResponse(
                        success=True,
                        data=response.json() if response.content else None,
                        status_code=response.status_code,
                        message="Success",
                        rate_limit_info=rate_limit_info
                    )
                
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay * (2 ** attempt)))
                    self.logger.warning(f"Rate limited, waiting {retry_after}s before retry {attempt + 1}")
                    time.sleep(retry_after)
                    continue
                
                elif response.status_code in [500, 502, 503, 504]:  # Server errors
                    if attempt < self.retry_attempts - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        self.logger.warning(f"Server error {response.status_code}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                
                # Client errors or final attempt
                error_message = self._parse_error_message(response)
                return APIResponse(
                    success=False,
                    data=None,
                    status_code=response.status_code,
                    message=error_message,
                    rate_limit_info=rate_limit_info
                )
                
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Request exception: {e}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    return APIResponse(
                        success=False,
                        data=None,
                        status_code=0,
                        message=f"Request failed: {str(e)}"
                    )
        
        return APIResponse(
            success=False,
            data=None,
            status_code=0,
            message="Max retries exceeded"
        )

    def _parse_rate_limit_headers(self, headers: Dict[str, str]) -> Optional[RateLimitInfo]:
        """Parse rate limit information from response headers"""
        try:
            if 'X-RateLimit-Remaining' in headers:
                remaining = int(headers['X-RateLimit-Remaining'])
                reset_time = datetime.fromtimestamp(int(headers.get('X-RateLimit-Reset', time.time())))
                total = int(headers.get('X-RateLimit-Limit', self.rate_limit_rpm))
                
                return RateLimitInfo(remaining, reset_time, total)
        except (ValueError, KeyError):
            pass
        return None

    def _parse_error_message(self, response: requests.Response) -> str:
        """Extract meaningful error message from response"""
        try:
            error_data = response.json()
            
            # Handle different error response formats
            if 'message' in error_data:
                message = error_data['message']
                if 'errors' in error_data:
                    # Add detailed validation errors
                    errors = error_data['errors']
                    if isinstance(errors, dict):
                        error_details = []
                        for field, field_errors in errors.items():
                            if isinstance(field_errors, list):
                                error_details.extend([f"{field}: {err}" for err in field_errors])
                            else:
                                error_details.append(f"{field}: {field_errors}")
                        if error_details:
                            message += f" - {'; '.join(error_details)}"
                return message
            
            elif 'error' in error_data:
                return error_data['error']
            
            else:
                return f"API error: {response.status_code}"
                
        except (json.JSONDecodeError, KeyError):
            return f"HTTP {response.status_code}: {response.text[:200]}..."

    # Core API Methods

    def upload_image(self, file_name: str, contents: str) -> APIResponse:
        """Upload image to Printify media library"""
        data = {
            "file_name": file_name,
            "contents": contents
        }
        return self._make_request("POST", "/uploads/images.json", data)

    def create_product(self, product_data: Dict[str, Any]) -> APIResponse:
        """Create a new product"""
        # Add GPSR compliance field if not present (latest API feature)
        if 'safety_information' not in product_data:
            product_data['safety_information'] = ""
        
        url = f"/shops/{self.shop_id}/products.json"
        return self._make_request("POST", url, product_data, is_product_creation=True)

    def get_products(self, page: int = 1, limit: int = 50) -> APIResponse:
        """Get products with pagination (updated limit)"""
        url = f"/shops/{self.shop_id}/products.json?page={page}&limit={limit}"
        return self._make_request("GET", url)

    def get_product(self, product_id: str) -> APIResponse:
        """Get single product details"""
        url = f"/shops/{self.shop_id}/products/{product_id}.json"
        return self._make_request("GET", url)

    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> APIResponse:
        """Update existing product"""
        url = f"/shops/{self.shop_id}/products/{product_id}.json"
        return self._make_request("PUT", url, product_data)

    def delete_product(self, product_id: str) -> APIResponse:
        """Delete a product"""
        url = f"/shops/{self.shop_id}/products/{product_id}.json"
        return self._make_request("DELETE", url)

    def get_catalog_blueprints(self) -> APIResponse:
        """Get available product blueprints"""
        return self._make_request("GET", "/catalog/blueprints.json")

    def get_blueprint_variants(self, blueprint_id: int, provider_id: int, 
                              show_out_of_stock: bool = False) -> APIResponse:
        """Get variants for blueprint and provider"""
        url = f"/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json"
        if show_out_of_stock:
            url += "?show-out-of-stock=1"
        return self._make_request("GET", url)

    def get_blueprint_providers(self, blueprint_id: int) -> APIResponse:
        """Get print providers for a blueprint"""
        url = f"/catalog/blueprints/{blueprint_id}/print_providers.json"
        return self._make_request("GET", url)

    # V2 API Methods (Latest Features)

    def get_shipping_info_v2(self, blueprint_id: int, provider_id: int, 
                           shipping_type: str = "standard") -> APIResponse:
        """Get shipping information using V2 API"""
        url = f"/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/shipping/{shipping_type}.json"
        return self._make_request("GET", url, api_version=APIVersion.V2)

    def get_economy_shipping_v2(self, blueprint_id: int, provider_id: int) -> APIResponse:
        """Get economy shipping info (V2 only feature)"""
        return self.get_shipping_info_v2(blueprint_id, provider_id, "economy")

    # Enhanced Helper Methods

    def validate_credentials(self) -> Tuple[bool, str]:
        """Validate API credentials"""
        response = self._make_request("GET", "/shops.json")
        if response.success:
            shops = response.data
            if any(shop['id'] == int(self.shop_id) for shop in shops):
                return True, "Credentials valid"
            else:
                return False, f"Shop ID {self.shop_id} not found in accessible shops"
        else:
            return False, f"Authentication failed: {response.message}"

    def get_shop_info(self) -> APIResponse:
        """Get shop information"""
        return self._make_request("GET", f"/shops/{self.shop_id}.json")

    def bulk_upload_images(self, images: List[Tuple[str, str]]) -> List[APIResponse]:
        """Upload multiple images efficiently"""
        results = []
        for file_name, contents in images:
            response = self.upload_image(file_name, contents)
            results.append(response)
            
            # Small delay between uploads to be nice to the API
            time.sleep(0.1)
        
        return results

    def get_product_templates(self) -> Dict[str, Any]:
        """Get common product templates with current pricing and features"""
        templates = {
            "t_shirt": {
                "blueprint_id": 384,
                "name": "Unisex Heavy Cotton Tee",
                "print_positions": ["front", "back"],
                "recommended_variants": []
            },
            "poster": {
                "blueprint_id": 5,
                "name": "Poster",
                "print_positions": ["front"],
                "recommended_variants": []
            },
            "mug": {
                "blueprint_id": 9,
                "name": "Coffee Mug",
                "print_positions": ["front"],
                "recommended_variants": []
            },
            "canvas": {
                "blueprint_id": 6,
                "name": "Canvas",
                "print_positions": ["front"],
                "recommended_variants": []
            },
            "phone_case": {
                "blueprint_id": 12,
                "name": "Phone Case",
                "print_positions": ["front"],
                "recommended_variants": []
            }
        }
        
        # Populate with actual data from API
        for template_name, template_data in templates.items():
            blueprint_id = template_data["blueprint_id"]
            
            # Get providers
            providers_response = self.get_blueprint_providers(blueprint_id)
            if providers_response.success and providers_response.data:
                # Use first available provider for template
                provider = providers_response.data[0]
                template_data["default_provider_id"] = provider["id"]
                
                # Get variants
                variants_response = self.get_blueprint_variants(blueprint_id, provider["id"])
                if variants_response.success and variants_response.data:
                    variants = variants_response.data.get("variants", [])
                    template_data["recommended_variants"] = [v["id"] for v in variants[:5]]  # First 5 variants
        
        return templates

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'user_agent': 'Printify-Automation-Tool',
        'rate_limit_rpm': 600,
        'retry_attempts': 3
    }
    
    # Initialize client (replace with actual credentials)
    client = PrintifyAPIClient("your_token", "your_shop_id", config)
    
    # Validate credentials
    is_valid, message = client.validate_credentials()
    print(f"Credentials valid: {is_valid} - {message}")
    
    # Get product templates
    templates = client.get_product_templates()
    print(f"Available templates: {list(templates.keys())}")
    
    # Clean up
    client.close()