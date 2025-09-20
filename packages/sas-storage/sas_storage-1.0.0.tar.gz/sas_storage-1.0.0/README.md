# Azure Storage Helper Library

A comprehensive Python helper library for Azure Storage Blob and Queue operations with enhanced SAS token generation, async/sync support, and enterprise-grade functionality.

## Overview

This library provides a simplified interface for Azure Storage operations with built-in best practices for authentication, error handling, and SAS token generation. It supports both synchronous and asynchronous operations with full feature parity, making it suitable for various application architectures from simple scripts to high-performance applications.

## Key Features

### Authentication & Security

- **Multiple Authentication Methods**: DefaultAzureCredential, ManagedIdentity, Account Keys, Connection Strings
- **Automatic Credential Detection**: Smart credential chain with fallback mechanisms
- **Enhanced Error Handling**: Detailed error messages with troubleshooting guidance
- **Secure Session Management**: Proper HTTP session cleanup and resource management

### SAS Token Generation

- **User Delegation SAS**: Modern Azure AD-based SAS tokens with enhanced security
- **Account Key SAS**: Traditional account key-based tokens for backward compatibility
- **Clock Skew Protection**: Automatic time buffer to prevent authentication failures
- **Flexible Permissions**: Granular permission control for different operations
- **Container & Blob Level**: Generate SAS tokens for both containers and individual blobs

### Blob Operations

- **Container Management**: Create, delete (with force delete), list, and check container existence
- **Blob Operations**: Upload, download, copy, move, and delete blobs with metadata support
- **File Operations**: Direct file upload/download with automatic path handling
- **Directory-like Navigation**: Hierarchical listing with prefix support and delimiter handling
- **Metadata Management**: Get, set, and manage blob metadata and properties
- **Batch Operations**: Process multiple files simultaneously with progress tracking
- **Search Functionality**: Search blobs by name, metadata, or content patterns
- **Content Type Detection**: Automatic content type detection based on file extensions
- **Large File Upload**: Progress tracking and chunked upload for large files
- **Blob Snapshots**: Create and manage blob snapshots (sync version)
- **Blob Tiers**: Hot, Cool, and Archive tier management

### Queue Operations & Management

- **Queue Management**: Create, delete, list, clear, and manage queue properties
- **Message Operations**: Send, receive, peek, delete, and update messages
- **Batch Message Operations**: Process multiple messages simultaneously with concurrency control
- **Message Encoding**: Support for text, binary, and JSON message formats with automatic serialization
- **Visibility Timeout**: Configurable message visibility and processing timeouts
- **Worker Patterns**: Built-in support for common queue processing patterns

### Performance & Reliability

- **Async/Sync Feature Parity**: Complete feature compatibility between async and sync versions
- **Retry Logic**: Built-in retry mechanisms with exponential backoff
- **Connection Pooling**: Efficient HTTP connection management
- **Concurrent Operations**: High-performance parallel processing capabilities
- **Resource Cleanup**: Automatic session and resource cleanup
- **Memory Efficient**: Streaming operations for large files

### Developer Experience

- **Comprehensive Logging**: Configurable logging levels with detailed operation tracking
- **Type Hints**: Full type annotation support for better IDE experience
- **Extensive Test Coverage**: 95%+ test coverage with real Azure resource integration
- **Example Library**: 25+ practical examples covering common use cases
- **API Documentation**: Microsoft SDK-style documentation with detailed parameter descriptions
- **Error Handling**: Informative error messages with suggested solutions

## Installation

```bash
# Using pip
pip install sas-storage

# Using uv (recommended)
uv add sas-storage

# For development
uv sync --dev
```

## Recent Updates & Improvements

### Version Improvements

- **Parameter Consistency**: Fixed parameter naming inconsistencies between async and sync variants
  - `AsyncStorageBlobHelper.download_file()` now correctly uses `local_file_path` parameter
  - Consistent method signatures across all helper classes
- **Test Suite Enhancements**: Comprehensive test coverage with real Azure Storage resources
  - Fixed test parameter mismatches in blob upload operations
  - Corrected property assertions to match actual Azure Storage responses
  - All tests now pass with both sync and async implementations
- **Error Handling**: Enhanced error messages and validation throughout the library
- **Documentation**: Updated examples and documentation to reflect current API

### Breaking Changes

- **Parameter Names**: Some method parameters have been standardized for consistency
  - `download_file()` methods now consistently use `local_file_path` instead of `file_path`
  - Removed invalid `content_type` parameters from certain upload operations
- **Return Values**: Standardized return value structures for property methods

## Quick Start

### Basic Blob Operations

```python
from sas.storage.blob import AsyncStorageBlobHelper

async def example():
    async with AsyncStorageBlobHelper(account_name="myaccount") as helper:
        # Upload a file
        await helper.upload_blob("container", "file.txt", "Hello World!")
        
        # Generate SAS URL
        sas_url = await helper.generate_blob_sas_url(
            container_name="container",
            blob_name="file.txt",
            permissions="r",
            expiry_hours=1
        )
        
        # List blobs
        blobs = await helper.list_blobs("container")
```

### Queue Operations

```python
from sas.storage.queue import AsyncStorageQueueHelper

async def queue_example():
    async with AsyncStorageQueueHelper(account_name="myaccount") as helper:
        # Send message
        await helper.send_message("myqueue", "Hello Queue!")
        
        # Receive messages
        messages = await helper.receive_messages("myqueue")
        
        # Peek without removing
        peeked = await helper.peek_messages("myqueue")
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```properties
# Option 1: Use Account Name with Azure AD (recommended)
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account

# Option 2: Use Connection String
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# Optional: Logging level
LOGGING_LEVEL=INFO
```

### Authentication Setup

The library automatically detects available credentials in this order:

1. **DefaultAzureCredential** (recommended for production)
   - Managed Identity
   - Azure CLI
   - Azure PowerShell
   - Environment variables

2. **Account Key** (from connection string or environment)

3. **Manual credential configuration**

## Testing

This library includes comprehensive test suites for both synchronous and asynchronous operations with over 95% code coverage. All major functionality is tested against real Azure Storage resources to ensure reliability and compatibility.

### Recent Improvements

- **Parameter Consistency**: Fixed parameter naming consistency between async and sync variants (e.g., `download_file` now uses `local_file_path` consistently)
- **Enhanced Test Coverage**: Comprehensive testing of all blob and queue operations with real Azure resources
- **Error Handling**: Improved error handling and validation in both sync and async helpers
- **Method Signature Validation**: All test methods now correctly match the actual helper method signatures

### Test Structure

- **Sync Tests** (`test_sync_helpers.py`): Complete test coverage for `StorageBlobHelper` and `StorageQueueHelper`
- **Async Tests** (`test_async_helpers.py`): Full test coverage for `AsyncStorageBlobHelper` and `AsyncStorageQueueHelper`
- **Integration Tests**: Real Azure Storage operations including container management, blob operations, and queue processing
- **Authentication Tests**: Multiple authentication method validation including DefaultAzureCredential and account keys

### Running Tests

Before running tests, please ensure you have set up your Azure Storage account and prepare the environment variables or `.env` file

#### .env File

```env
# Azure Storage Integration Test Configuration
# Copy this file to .env and fill in your actual values

# Option 1: Use Connection String (recommended for development)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT_NAME;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net

# Option 2: Use Account Name with Managed Identity (for production)
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
```

#### Test Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_sync_helpers.py
uv run pytest tests/test_async_helpers.py

# Run with coverage report
uv run pytest --cov=src --cov-report=html
```

### Test Coverage

The test suite covers:

- **Container Operations**: Create, delete, list, exists checking
- **Blob Operations**: Upload, download, copy, move, delete, metadata management
- **File Operations**: Direct file upload/download with various file types
- **Directory Operations**: Hierarchical navigation and prefix-based operations
- **SAS Token Generation**: User delegation and account key-based tokens
- **Queue Operations**: Message send/receive, batch operations, queue management
- **Authentication**: Multiple credential types and fallback mechanisms
- **Error Handling**: Exception scenarios and edge cases
- **Async/Sync Parity**: Feature compatibility between async and sync versions



## Project Structure

```text
src/
├── sas/
│   └── storage/
│       ├── shared_config.py       # Shared configuration and constants
│       ├── blob/
│       │   ├── __init__.py
│       │   ├── async_helper.py    # AsyncStorageBlobHelper class
│       │   ├── helper.py          # StorageBlobHelper class
│       │   └── config.py          # Blob-specific configuration
│       └── queue/
│           ├── __init__.py
│           ├── async_helper.py    # AsyncStorageQueueHelper class
│           └── helper.py          # StorageQueueHelper class
tests/
├── test_async_helpers.py          # Comprehensive async operation tests
└── test_sync_helpers.py           # Comprehensive sync operation tests
examples/
├── blob/                          # 10+ blob operation examples
│   ├── 01_basic_upload_download.py
│   ├── 02_upload_file.py
│   ├── 03_create_container.py
│   ├── 04_generate_sas.py
│   ├── 05_list_blobs.py
│   ├── 06_delete_operations.py
│   ├── 07_metadata.py
│   ├── 08_batch_upload.py
│   ├── 09_check_exists.py
│   └── 10_comparison_with_sdk.py
└── queue/                         # 9+ queue operation examples
    ├── 01_basic_send_receive.py
    ├── 02_create_queue.py
    ├── 03_json_messages.py
    ├── 04_batch_operations.py
    ├── 05_message_visibility.py
    ├── 06_peek_messages.py
    ├── 07_queue_management.py
    ├── 08_clear_and_cleanup.py
    └── 09_worker_pattern.py
```

## Requirements

- Python 3.12 or higher
- Azure Storage account
- Storage Blob Contributor role
- Storage Queue Contributor role

## Dependencies

Core dependencies:

- `azure-storage-blob>=12.20.0`
- `azure-storage-queue>=12.9.0`
- `azure-identity>=1.15.0`
- `azure-core>=1.29.0`
- `aiofiles>=23.2.0`
- `aiohttp>=3.8.0`

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/sas-storage.git
cd sas-storage

# Install development dependencies
uv sync --dev
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
