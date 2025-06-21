# Architecture Documentation

## System Overview

The Printify Automation Tool is designed as a modular, event-driven system that processes AI-generated images with minimal user interaction.

## Design Principles

1. **Automation First**: Minimize user interaction beyond initial configuration
2. **Configuration Driven**: All behavior controlled through YAML configuration
3. **Fault Tolerant**: Robust error handling and recovery mechanisms
4. **Modular Design**: Clear separation of concerns between components
5. **Scalable**: Support for concurrent processing and multiple product types

## Core Components

### 1. Configuration Management (`config.py`)

**Purpose**: Centralized configuration handling with validation

**Key Classes**:
- `Config`: Main configuration loader and validator
- `PrintifyConfig`: Printify API credentials and settings
- `ProductTemplate`: Product template definitions
- `FolderConfig`: Folder monitoring configuration

**Features**:
- YAML-based configuration with full validation
- Automatic folder structure creation
- Configuration persistence and reloading
- Type safety with Pydantic models

### 2. File System Monitoring (`monitor.py`)

**Purpose**: Watch configured folders for new/modified images

**Key Classes**:
- `ImageHandler`: File system event handler
- `Observer`: File system watcher (from watchdog library)

**Features**:
- Real-time file system monitoring
- Image file filtering (PNG, JPG, JPEG)
- Event queuing for processing pipeline
- Support for multiple folder monitoring

### 3. Main Automation Engine (`main.py`)

**Purpose**: Orchestrates the entire automation pipeline

**Key Classes**:
- `PrintifyAutomation`: Main automation controller

**Features**:
- Queue-based processing pipeline
- Duplicate detection and tracking
- Process state persistence
- Graceful shutdown handling

## Data Flow

```
1. User drops image in monitored folder
2. File system monitor detects change
3. Event added to processing queue
4. Main engine processes queue item:
   a. Extract metadata/prompt from image
   b. Generate product title and tags
   c. Optimize image for Printify
   d. Create product via Printify API
   e. Move image to processed/failed folder
5. Update processing database
6. Continue monitoring for new files
```

## File Organization

```
printify-automation/
├── config.py              # Configuration management
├── monitor.py              # File system monitoring
├── main.py                # Main automation engine
├── requirements.txt        # Python dependencies
├── config.yaml            # User configuration
├── processed_images.json  # Processing state database
└── logs/                  # Application logs
    ├── automation.log
    └── errors.log
```

## Configuration Schema

```yaml
printify:                   # Printify API configuration
  access_token: string
  shop_id: integer
  base_url: string

folders:                    # List of monitored folders
  - path: string           # Folder path to monitor
    template:              # Product template
      blueprint_id: int    # Printify product type
      print_provider_id: int
      base_price: int      # Price in cents
      variants: list       # Available variants
      print_areas: dict    # Print area configuration
    create_processed_folder: bool
    create_failed_folder: bool
```

## Error Handling Strategy

### 1. Configuration Errors
- Validation at startup
- Clear error messages for common misconfigurations
- Graceful fallbacks where possible

### 2. API Errors
- Exponential backoff retry mechanism
- Rate limiting compliance
- Detailed error logging with context

### 3. Image Processing Errors
- File format validation
- Metadata extraction fallbacks
- Image optimization error recovery

### 4. File System Errors
- Permission handling
- Disk space monitoring
- Corrupted file detection

## State Management

### Processing Database (`processed_images.json`)
Tracks all processed images to prevent duplicates:

```json
{
  "image_path": {
    "processed_at": "2024-01-15T10:30:00",
    "status": "success|failed|pending",
    "product_id": "printify_product_id",
    "error_message": "error_details"
  }
}
```

### Folder Structure
- `processed/`: Successfully created products
- `failed/`: Images that failed processing
- Original folder: New images to process

## Security Considerations

1. **API Credentials**: Stored in configuration file (should be secured)
2. **File Permissions**: Automatic folder creation with appropriate permissions
3. **Input Validation**: All configuration and file inputs validated
4. **Error Logging**: Sensitive data excluded from logs

## Performance Characteristics

### Current Implementation
- **Processing Mode**: Sequential (one image at a time)
- **Memory Usage**: Low (processes one image at a time)
- **API Rate Limiting**: Built-in respect for Printify limits

### Future Optimizations
- **Concurrent Processing**: Multiple images simultaneously
- **Batch Operations**: Group API calls where possible
- **Caching**: Cache frequently accessed API data
- **Connection Pooling**: Reuse HTTP connections

## Extension Points

### 1. Metadata Processing
Current: Basic EXIF extraction
Future: AI-powered prompt analysis, categorization

### 2. Image Processing
Current: Basic optimization
Future: Advanced editing, multiple print areas, templates

### 3. Product Management
Current: Simple creation
Future: Bulk editing, templating, analytics

### 4. Integration
Current: Printify only
Future: Multiple platforms, webhooks, external APIs

## Monitoring and Logging

### Log Levels
- **INFO**: Normal operation events
- **WARNING**: Non-critical issues
- **ERROR**: Processing failures
- **DEBUG**: Detailed debugging information

### Metrics to Track
- Processing success/failure rates
- API response times
- Queue depth and processing time
- Error patterns and frequencies

## Testing Strategy

### Unit Tests
- Configuration validation
- Metadata extraction
- Error handling scenarios

### Integration Tests
- End-to-end processing pipeline
- API integration
- File system operations

### Manual Testing
- Real image processing
- Error scenario validation
- Performance under load

This architecture provides a solid foundation for the automation tool while maintaining flexibility for future enhancements.
