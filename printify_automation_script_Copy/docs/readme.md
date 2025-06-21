# Printify Automation Tool

An automated system for processing AI-generated images and creating Printify products with minimal user interaction.

## Overview

This tool monitors designated folders for new AI-generated images, extracts prompts from image metadata, and automatically creates Printify products with optimized titles, descriptions, and tags.

## Key Features

- **Automated File Monitoring**: Watches configured folders for new/modified images
- **Metadata Processing**: Extracts AI prompts from image EXIF data
- **Intelligent Title Generation**: Creates product titles from AI prompts
- **Automatic Tag Extraction**: Generates relevant tags from prompt content
- **Batch Processing**: Handles multiple images concurrently
- **Error Recovery**: Robust error handling with retry mechanisms
- **Configuration-Driven**: YAML-based configuration for easy setup

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy and configure the settings:
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your Printify credentials and folder paths
   ```

3. Run the automation:
   ```bash
   python main.py
   ```

4. Drop AI-generated images into your configured folders and watch them get processed automatically!

## Project Structure

```
printify-automation/
├── README.md
├── SETUP.md
├── ARCHITECTURE.md
├── API_REFERENCE.md
├── config.example.yaml
├── requirements.txt
├── main.py
├── config.py
├── monitor.py
└── logs/
```

## Configuration

The system uses YAML configuration files to define:
- Printify API credentials
- Monitored folders and their product templates
- Processing rules and automation settings

See [SETUP.md](SETUP.md) for detailed configuration instructions.

## Architecture

The system follows a modular architecture with clear separation of concerns:
- Configuration management
- File system monitoring
- Image processing
- Printify API integration
- Error handling and logging

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design information.

## Requirements

- Python 3.8+
- Printify API access token
- Images with EXIF metadata containing AI prompts

## Support

For detailed setup instructions, see [SETUP.md](SETUP.md).
For API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
