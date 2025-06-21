"""
Advanced Error Handling and Recovery System
Provides comprehensive error handling, retry logic, and user-friendly error reporting
"""

import logging
import traceback
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    NETWORK = "network"
    API = "api"
    FILE_IO = "file_io"
    IMAGE_PROCESSING = "image_processing"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"

@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    timestamp: datetime = None
    context: Dict[str, Any] = None
    recoverable: bool = True
    recovery_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.context is None:
            self.context = {}
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []

class ErrorHandler:
    def __init__(self, log_file: str = "error_log.json"):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.error_history: List[ErrorInfo] = []
        self.error_patterns = self._initialize_error_patterns()
        
        # Load existing error history
        self._load_error_history()
        
        # Statistics
        self.error_counts = {category: 0 for category in ErrorCategory}
        self.recovery_success_rate = {}

    def _initialize_error_patterns(self) -> Dict[str, Dict]:
        """Initialize common error patterns and their handling strategies"""
        return {
            # Network errors
            "connection_timeout": {
                "category": ErrorCategory.NETWORK,
                "severity": ErrorSeverity.WARNING,
                "recoverable": True,
                "retry_strategy": "exponential_backoff",
                "max_retries": 3,
                "suggestions": [
                    "Check internet connection",
                    "Verify Printify API status",
                    "Try again in a few minutes"
                ]
            },
            "connection_refused": {
                "category": ErrorCategory.NETWORK,
                "severity": ErrorSeverity.ERROR,
                "recoverable": True,
                "retry_strategy": "linear_backoff",
                "max_retries": 2,
                "suggestions": [
                    "Check internet connection",
                    "Verify API endpoint URL",
                    "Contact system administrator"
                ]
            },
            
            # API errors
            "rate_limit_exceeded": {
                "category": ErrorCategory.RATE_LIMIT,
                "severity": ErrorSeverity.WARNING,
                "recoverable": True,
                "retry_strategy": "wait_and_retry",
                "max_retries": 5,
                "suggestions": [
                    "Wait for rate limit reset",
                    "Reduce upload frequency",
                    "Consider batch processing"
                ]
            },
            "invalid_credentials": {
                "category": ErrorCategory.AUTHENTICATION,
                "severity": ErrorSeverity.CRITICAL,
                "recoverable": False,
                "suggestions": [
                    "Check access token in config.json",
                    "Verify shop ID is correct",
                    "Generate new API token from Printify dashboard"
                ]
            },
            "invalid_request_data": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.ERROR,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Check product configuration",
                    "Verify image meets requirements",
                    "Review API documentation"
                ]
            },
            
            # File I/O errors
            "file_not_found": {
                "category": ErrorCategory.FILE_IO,
                "severity": ErrorSeverity.ERROR,
                "recoverable": False,
                "suggestions": [
                    "Check file path is correct",
                    "Verify file exists",
                    "Check file permissions"
                ]
            },
            "permission_denied": {
                "category": ErrorCategory.FILE_IO,
                "severity": ErrorSeverity.ERROR,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Check file permissions",
                    "Run with appropriate privileges",
                    "Verify write access to directory"
                ]
            },
            
            # Image processing errors
            "image_too_large": {
                "category": ErrorCategory.IMAGE_PROCESSING,
                "severity": ErrorSeverity.WARNING,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Image will be automatically resized",
                    "Consider using smaller images",
                    "Check image optimization settings"
                ]
            },
            "corrupted_image": {
                "category": ErrorCategory.IMAGE_PROCESSING,
                "severity": ErrorSeverity.ERROR,
                "recoverable": False,
                "suggestions": [
                    "Try a different image file",
                    "Check if image file is corrupted",
                    "Convert image to supported format"
                ]
            },
            "unsupported_format": {
                "category": ErrorCategory.IMAGE_PROCESSING,
                "severity": ErrorSeverity.WARNING,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Convert to JPEG or PNG format",
                    "Use supported image formats only",
                    "Check image file extension"
                ]
            },
            
            # Configuration errors
            "missing_config": {
                "category": ErrorCategory.CONFIGURATION,
                "severity": ErrorSeverity.CRITICAL,
                "recoverable": False,
                "suggestions": [
                    "Create config.json file",
                    "Add required API credentials",
                    "Use configuration wizard"
                ]
            },
            "invalid_config": {
                "category": ErrorCategory.CONFIGURATION,
                "severity": ErrorSeverity.ERROR,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Check config.json syntax",
                    "Verify all required fields",
                    "Use configuration template"
                ]
            },
            
            # Additional API errors
            "blueprint_not_found": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.ERROR,
                "recoverable": False,
                "suggestions": [
                    "Check blueprint ID is correct",
                    "Verify product is available in catalog",
                    "Use a different product blueprint"
                ]
            },
            "provider_not_available": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.WARNING,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Try a different print provider",
                    "Check provider availability",
                    "Contact Printify support"
                ]
            },
            "variant_out_of_stock": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.WARNING,
                "recoverable": True,
                "max_retries": 1,
                "suggestions": [
                    "Try different variant sizes/colors",
                    "Check stock availability",
                    "Use auto-variant selection"
                ]
            },
            
            # Image upload specific errors
            "image_upload_failed": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.ERROR,
                "recoverable": True,
                "max_retries": 3,
                "suggestions": [
                    "Check image file integrity",
                    "Try re-uploading the image",
                    "Verify image meets requirements"
                ]
            },
            "image_too_small": {
                "category": ErrorCategory.IMAGE_PROCESSING,
                "severity": ErrorSeverity.ERROR,
                "recoverable": False,
                "suggestions": [
                    "Use higher resolution image",
                    "Check minimum size requirements",
                    "Try AI upscaling tools"
                ]
            },
            
            # Product creation errors
            "product_creation_failed": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.ERROR,
                "recoverable": True,
                "max_retries": 2,
                "suggestions": [
                    "Check product configuration",
                    "Verify all required fields",
                    "Try with different settings"
                ]
            },
            "duplicate_product": {
                "category": ErrorCategory.API,
                "severity": ErrorSeverity.WARNING,
                "recoverable": False,
                "suggestions": [
                    "Product may already exist",
                    "Check existing products",
                    "Use different title or settings"
                ]
            }
        }

    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """Main error handling method"""
        error_info = self._analyze_error(error, context or {})
        self._log_error(error_info)
        self.error_history.append(error_info)
        self.error_counts[error_info.category] += 1
        
        # Save to persistent storage
        self._save_error_history()
        
        return error_info

    def _analyze_error(self, error: Exception, context: Dict[str, Any]) -> ErrorInfo:
        """Analyze error and determine category, severity, and recovery options"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Try to match against known patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            if self._matches_pattern(error_str, pattern_name):
                return ErrorInfo(
                    category=pattern_info["category"],
                    severity=pattern_info["severity"],
                    message=str(error),
                    details=self._get_error_details(error),
                    context=context,
                    recoverable=pattern_info.get("recoverable", True),
                    recovery_suggestions=pattern_info.get("suggestions", [])
                )
        
        # Default categorization based on error type
        category, severity = self._categorize_by_type(error_type, error_str)
        
        return ErrorInfo(
            category=category,
            severity=severity,
            message=str(error),
            details=self._get_error_details(error),
            context=context,
            recoverable=self._is_potentially_recoverable(error_type),
            recovery_suggestions=self._get_generic_suggestions(category)
        )

    def _matches_pattern(self, error_str: str, pattern_name: str) -> bool:
        """Check if error matches a known pattern"""
        pattern_keywords = {
            "connection_timeout": ["timeout", "timed out"],
            "connection_refused": ["connection refused", "connection failed"],
            "rate_limit_exceeded": ["rate limit", "too many requests", "429"],
            "invalid_credentials": ["unauthorized", "401", "invalid token"],
            "invalid_request_data": ["bad request", "400", "validation failed"],
            "file_not_found": ["file not found", "no such file"],
            "permission_denied": ["permission denied", "access denied"],
            "image_too_large": ["image too large", "file size", "decompression bomb"],
            "corrupted_image": ["cannot identify image", "truncated", "corrupted"],
            "unsupported_format": ["unsupported format", "cannot determine format"],
            "missing_config": ["config not found", "no such file.*config"],
            "invalid_config": ["json", "invalid syntax", "decode error"],
            "blueprint_not_found": ["blueprint not found", "blueprint.*not.*exist", "404.*blueprint"],
            "provider_not_available": ["provider not available", "provider.*not.*found"],
            "variant_out_of_stock": ["out of stock", "variant.*not.*available", "stock"],
            "image_upload_failed": ["upload failed", "upload.*error", "media.*error"],
            "image_too_small": ["image too small", "below.*minimum", "resolution.*low"],
            "product_creation_failed": ["product.*creation.*failed", "product.*error"],
            "duplicate_product": ["duplicate", "already.*exists", "conflict"]
        }
        
        keywords = pattern_keywords.get(pattern_name, [])
        return any(keyword in error_str for keyword in keywords)

    def _categorize_by_type(self, error_type: str, error_str: str) -> tuple:
        """Categorize error by exception type"""
        if error_type in ["ConnectionError", "Timeout", "HTTPError"]:
            return ErrorCategory.NETWORK, ErrorSeverity.WARNING
        elif error_type in ["FileNotFoundError", "PermissionError", "IOError"]:
            return ErrorCategory.FILE_IO, ErrorSeverity.ERROR
        elif error_type in ["PIL.UnidentifiedImageError", "OSError"]:
            return ErrorCategory.IMAGE_PROCESSING, ErrorSeverity.WARNING
        elif error_type in ["JSONDecodeError", "KeyError", "ValueError"]:
            return ErrorCategory.CONFIGURATION, ErrorSeverity.ERROR
        else:
            return ErrorCategory.API, ErrorSeverity.ERROR

    def _is_potentially_recoverable(self, error_type: str) -> bool:
        """Determine if error type is potentially recoverable"""
        non_recoverable_types = [
            "FileNotFoundError", "PermissionError", "PIL.UnidentifiedImageError"
        ]
        return error_type not in non_recoverable_types

    def _get_error_details(self, error: Exception) -> str:
        """Get detailed error information including traceback"""
        return traceback.format_exc()

    def _get_generic_suggestions(self, category: ErrorCategory) -> List[str]:
        """Get generic recovery suggestions for error category"""
        suggestions = {
            ErrorCategory.NETWORK: [
                "Check internet connection",
                "Retry the operation",
                "Contact system administrator if issue persists"
            ],
            ErrorCategory.API: [
                "Check API credentials",
                "Verify request data",
                "Review API documentation"
            ],
            ErrorCategory.FILE_IO: [
                "Check file permissions",
                "Verify file path",
                "Ensure sufficient disk space"
            ],
            ErrorCategory.IMAGE_PROCESSING: [
                "Try a different image",
                "Check image format",
                "Verify image is not corrupted"
            ],
            ErrorCategory.CONFIGURATION: [
                "Check configuration file",
                "Verify all required settings",
                "Use configuration wizard"
            ]
        }
        return suggestions.get(category, ["Contact support for assistance"])

    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""
        log_message = f"[{error_info.category.value}] {error_info.message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _save_error_history(self):
        """Save error history to persistent storage"""
        try:
            # Keep only last 1000 errors to prevent file from growing too large
            recent_errors = self.error_history[-1000:]
            
            serializable_errors = []
            for error in recent_errors:
                serializable_errors.append({
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "message": error.message,
                    "details": error.details,
                    "timestamp": error.timestamp.isoformat(),
                    "context": error.context,
                    "recoverable": error.recoverable,
                    "recovery_suggestions": error.recovery_suggestions
                })
            
            with open(self.log_file, 'w') as f:
                json.dump(serializable_errors, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to save error history: {e}")

    def _load_error_history(self):
        """Load error history from persistent storage"""
        try:
            with open(self.log_file, 'r') as f:
                error_data = json.load(f)
            
            for error_dict in error_data:
                error_info = ErrorInfo(
                    category=ErrorCategory(error_dict["category"]),
                    severity=ErrorSeverity(error_dict["severity"]),
                    message=error_dict["message"],
                    details=error_dict.get("details"),
                    timestamp=datetime.fromisoformat(error_dict["timestamp"]),
                    context=error_dict.get("context", {}),
                    recoverable=error_dict.get("recoverable", True),
                    recovery_suggestions=error_dict.get("recovery_suggestions", [])
                )
                self.error_history.append(error_info)
                
        except (FileNotFoundError, json.JSONDecodeError):
            # No existing error history or corrupted file
            pass

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]
        
        summary = {
            "total_errors": len(recent_errors),
            "by_category": {},
            "by_severity": {},
            "most_common": [],
            "recovery_rate": 0
        }
        
        # Count by category and severity
        for error in recent_errors:
            category = error.category.value
            severity = error.severity.value
            
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        # Find most common error messages
        error_messages = {}
        for error in recent_errors:
            msg = error.message[:100]  # Truncate for grouping
            error_messages[msg] = error_messages.get(msg, 0) + 1
        
        summary["most_common"] = sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return summary

    def suggest_recovery_actions(self, error_info: ErrorInfo) -> List[str]:
        """Suggest specific recovery actions for an error"""
        actions = error_info.recovery_suggestions.copy()
        
        # Add context-specific suggestions
        if error_info.category == ErrorCategory.RATE_LIMIT:
            if error_info.context.get("request_count"):
                wait_time = error_info.context["request_count"] * 0.1
                actions.insert(0, f"Wait {wait_time:.1f} seconds before retrying")
        
        elif error_info.category == ErrorCategory.IMAGE_PROCESSING:
            if error_info.context.get("file_size"):
                size_mb = error_info.context["file_size"] / (1024 * 1024)
                if size_mb > 10:
                    actions.insert(0, f"Reduce image size (current: {size_mb:.1f}MB)")
        
        return actions

    def create_user_friendly_message(self, error_info: ErrorInfo) -> str:
        """Create a user-friendly error message"""
        if error_info.severity == ErrorSeverity.CRITICAL:
            prefix = "🚨 Critical Error:"
        elif error_info.severity == ErrorSeverity.ERROR:
            prefix = "❌ Error:"
        elif error_info.severity == ErrorSeverity.WARNING:
            prefix = "⚠️ Warning:"
        else:
            prefix = "ℹ️ Info:"
        
        message = f"{prefix} {error_info.message}"
        
        if error_info.recovery_suggestions:
            message += "\n\nSuggested actions:"
            for i, suggestion in enumerate(error_info.recovery_suggestions[:3], 1):
                message += f"\n{i}. {suggestion}"
        
        return message

# Context manager for error handling
class ErrorContext:
    def __init__(self, error_handler: ErrorHandler, context: Dict[str, Any] = None):
        self.error_handler = error_handler
        self.context = context or {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.error_handler.handle_error(exc_val, self.context)
        return False  # Don't suppress the exception

# Example usage
if __name__ == "__main__":
    error_handler = ErrorHandler()
    
    # Example error handling
    try:
        # Simulate an error
        raise ConnectionError("Connection to API failed")
    except Exception as e:
        error_info = error_handler.handle_error(e, {"operation": "upload_image", "retry_count": 1})
        print(error_handler.create_user_friendly_message(error_info))
    
    # Get error summary
    summary = error_handler.get_error_summary()
    print(f"\nError Summary: {summary}")