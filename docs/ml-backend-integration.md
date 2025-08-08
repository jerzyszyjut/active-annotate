# ML Backend Integration

This document describes the ML Backend API endpoints that have been added to integrate with Label Studio and custom ML models.

## Overview

The ML Backend integration provides a bridge between Label Studio and your custom ML models. It uses the Label Studio SDK to download training data and implements endpoints for prediction and training.

## Architecture

```
Label Studio ← Label Studio SDK ← Active Annotate ML API → Custom ML Backend
```

1. **Active Annotate ML API** uses Label Studio SDK to download training data
2. **Data is formatted** into ImageFolder format and zipped
3. **Custom ML Backend** receives the training file and trains the model
4. **Predictions** are served through the ML API endpoints

## Requirements

- **Label Studio SDK**: Required for downloading training data
- **Label Studio API Token**: Required for authentication
- **Custom ML Backend**: Must accept file uploads for training

## Installation

Install the Label Studio SDK:

```bash
pip install label-studio-sdk
```

## API Endpoints

### Base URL

All ML backend endpoints are prefixed with `/ml`

### 1. Health Check

- **GET** `/ml/health`
- **Description**: Check the health status of the ML backend
- **Response**:
  ```json
  {
    "status": "UP",
    "model_class": "CustomMLModel"
  }
  ```

### 2. Setup

- **POST** `/ml/setup`
- **Description**: Initialize ML model for a project
- **Request Body**:
  ```json
  {
    "project": "1.1640995200",
    "label_config": "<View>...</View>",
    "extra_params": {}
  }
  ```
- **Response**:
  ```json
  {
    "model_version": "1.0.0"
  }
  ```

### 3. Predict

- **POST** `/ml/predict`
- **Description**: Get predictions for tasks
- **Request Body**:
  ```json
  {
    "tasks": [
      {
        "id": 1,
        "data": {
          "image": "https://example.com/image.jpg"
        }
      }
    ],
    "model_version": "1.0.0",
    "project": "1.1640995200",
    "label_config": "<View>...</View>",
    "params": {
      "context": {}
    }
  }
  ```
- **Response**:
  ```json
  {
    "results": [
      [
        {
          "result": [
            {
              "value": { "choices": ["cat"] },
              "from_name": "choice",
              "to_name": "image",
              "type": "choices"
            }
          ],
          "score": 0.95,
          "model_version": "1.0.0"
        }
      ]
    ]
  }
  ```

### 4. Train

- **POST** `/ml/train`
- **Description**: Train ML model with data from Label Studio
- **Request Body**:
  ```json
  {
    "project_id": "1",
    "label_config": "<View>...</View>",
    "use_ground_truth": true,
    "extra_params": { "epochs": 10, "batch_size": 32 }
  }
  ```
- **Response**:
  ```json
  {
    "status": "started",
    "message": "Training initiated successfully",
    "task_id": "train_123"
  }
  ```

### 5. Metrics

- **GET** `/ml/metrics`
- **Description**: Get model performance metrics
- **Response**:
  ```json
  {}
  ```

## Configuration

Configure the following environment variables:

```env
# ML Backend URL - your custom ML backend that accepts file uploads
ML_BACKEND_URL=http://localhost:9000

# Label Studio configuration - required for training data download
LABEL_STUDIO_URL=http://localhost:8080
LABEL_STUDIO_TOKEN=your_api_token_here
```

### Getting Label Studio API Token

1. Go to your Label Studio instance (http://localhost:8080)
2. Click on your user profile in the top right
3. Go to "Account & Settings"
4. Copy the "Access Token" from the "API" section

## Custom ML Backend Requirements

Your custom ML backend should implement the following endpoints:

### 1. `/predict` (POST)

- **Input**: Tasks with data, project_id, label_config, context
- **Output**: Predictions in Label Studio format

### 2. `/setup` (POST)

- **Input**: Project configuration and label config
- **Output**: Model version

### 3. `/train` (POST)

- **Input**: Multipart form data with ZIP file containing ImageFolder dataset
- **Form Fields**:
  - `file`: ZIP file with ImageFolder format dataset
  - `project_id`: Label Studio project ID
  - `label_config`: Label configuration (optional)
  - Additional parameters as needed
- **Output**: Training task ID and status

### 4. `/health` (GET)

- **Output**: Health status

## Example Custom ML Backend Response

```python
# /predict endpoint response example
{
    "predictions": [
        {
            "result": [
                {
                    "value": {"choices": ["cat"]},
                    "from_name": "choice",
                    "to_name": "image",
                    "type": "choices"
                }
            ],
            "score": 0.95
        }
    ]
}
```

## Integration with Label Studio

1. **Start your custom ML backend** on port 8001 (or configure `ML_BACKEND_URL`)
2. **Start Active Annotate API** on port 8000
3. **Configure Label Studio** to use `http://localhost:8000/ml` as the ML backend URL

## Testing

Use the provided test script to verify the integration:

```bash
python examples/test_ml_backend.py
```

## Error Handling

The ML Backend API includes comprehensive error handling:

- **Connection failures** to custom ML backend result in empty predictions
- **Invalid requests** return appropriate HTTP error codes
- **Timeouts** are handled gracefully with fallback responses

## Supported Events

The webhook endpoint supports the following Label Studio events:

- `ANNOTATION_CREATED`
- `ANNOTATION_UPDATED`
- `ANNOTATION_DELETED`
- `START_TRAINING`

## Development

### File Structure

```
app/
├── api/endpoints/ml_backend.py    # API endpoints
├── models/ml_backend.py           # Pydantic models
├── services/ml_backend.py         # Business logic
└── core/config.py                 # Configuration
examples/
└── test_ml_backend.py            # Test script
```

### Adding New Features

1. **Update models** in `app/models/ml_backend.py`
2. **Add business logic** in `app/services/ml_backend.py`
3. **Create endpoints** in `app/api/endpoints/ml_backend.py`
4. **Test integration** with `examples/test_ml_backend.py`
