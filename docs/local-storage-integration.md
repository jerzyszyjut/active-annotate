# Local Storage Integration

This document explains the updated StorageService and its integration with Label Studio for handling local image directories.

## Overview

The StorageService has been modified to work with local directories containing images and automatically upload them to Label Studio projects using the Label Studio SDK.

## Key Changes

### StorageService (`app/services/storage.py`)

- **Local Directory Support**: Now works with local filesystem paths instead of URL-based paths
- **Validation**: Includes directory validation and image counting
- **Better Error Handling**: Comprehensive validation and logging
- **Path Objects**: Returns `pathlib.Path` objects for better file handling

### AnnotationToolClientService (`app/services/annotation_tool_client.py`)

- **Project Creation**: Can create new Label Studio projects
- **Local Image Upload**: Uploads local image files as base64-encoded data URLs
- **SDK Integration**: Uses the official Label Studio SDK client
- **Better Error Handling**: Comprehensive error handling and logging

### ProjectService (`app/services/project.py`)

- **Project Lifecycle**: Manages the complete project creation lifecycle
- **Batch Management**: Handles active learning batch selection and upload
- **Epoch Management**: Tracks and manages training epochs
- **Project Info**: Provides project status and information

## Usage

### Basic Usage

```python
from app.services.storage import StorageService
from app.services.annotation_tool_client import AnnotationToolClientService
from app.services.project import ProjectService

# 1. Set up local storage
storage = StorageService(path="/path/to/your/images")

# 2. Set up Label Studio client
annotation_client = AnnotationToolClientService(
    ip_address="localhost",
    port=8080,
    api_key="your_label_studio_token"
)

# 3. Create project service
project_service = ProjectService(
    storage=storage,
    annotation_service_config=annotation_client,
    name="my_project",
    al_batch=10,
    label_config=your_label_config,
)

# 4. Create project and upload initial batch
project_id = project_service.create_project_with_initial_batch()
```

### API Endpoints

The `/active-learning/start` endpoint now:

1. Validates the storage directory
2. Creates a new Label Studio project
3. Uploads the first batch of images
4. Returns the created project ID

The `/active-learning/check-tasks` endpoint now:

1. Creates a new project for the next epoch
2. Uploads the next batch of images
3. Updates the database with the new project ID

## Configuration

### Environment Variables

- `LABEL_STUDIO_URL`: URL of your Label Studio instance (default: http://localhost:8080)
- `LABEL_STUDIO_TOKEN`: API token for Label Studio authentication
- `STORAGE_PATH`: Path to your local image directory

### Storage Directory Structure

```
/your/storage/path/
├── image1.jpg
├── image2.png
├── image3.jpeg
└── ...
```

Supported image formats:

- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF
- WebP

## Example

See `examples/local_storage_example.py` for a complete working example.

## Requirements

- Label Studio instance running and accessible
- Valid Label Studio API token
- Local directory with image files
- Required Python packages: `label-studio-sdk`, `aiohttp`

## Migration from Previous Version

If you're migrating from the previous URL-based storage system:

1. **Update Storage Paths**: Change from URL paths to local filesystem paths
2. **Update API Calls**: The API now returns more detailed responses including project IDs
3. **Update Configuration**: Set up Label Studio connection parameters
4. **Test Storage**: Use the validation methods to ensure your storage is properly configured

## Error Handling

The updated services include comprehensive error handling:

- **Storage Validation**: Checks directory existence and permissions
- **Image Validation**: Validates image files and formats
- **Label Studio Connection**: Validates API connectivity and authentication
- **Upload Errors**: Handles individual image upload failures gracefully

## Logging

All services include detailed logging for debugging and monitoring:

- Storage operations
- Image processing
- Project creation
- Upload progress
- Error conditions

## Performance Considerations

- **Large Batches**: Consider batch size when uploading many images
- **Image Size**: Large images are base64-encoded, which increases payload size
- **Network**: Upload performance depends on Label Studio server connectivity
- **Storage**: Ensure adequate disk space for image processing
