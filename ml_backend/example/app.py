import logging
import os
import tempfile
import zipfile
import datetime
from io import BytesIO
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
import pytorch_lightning as pl
from fastapi import FastAPI, Request, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse

from model import ResNetImageClassificactionMLModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()


MODEL = ResNetImageClassificactionMLModel(weights_dir="model_weights")

# Global training status
TRAINING_STATUS = {
    "is_training": False,
    "last_training_time": None,
    "training_progress": None,
    "weights_dir": "model_weights",
}


def extract_zip_to_temp_dir(zip_file_content: bytes) -> str:
    """Extract zip file content to a temporary directory and return the path."""
    temp_dir = tempfile.mkdtemp()

    with BytesIO(zip_file_content) as zip_buffer:
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

    return temp_dir


def extract_zip(zip_path: str, extract_to: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


async def train_model_background(
    project_id: str, project_name: str, zip_content: bytes
):
    """Train a model in the background with the provided ZIP file content."""
    global MODEL, TRAINING_STATUS

    try:
        # Update training status
        TRAINING_STATUS["is_training"] = True
        TRAINING_STATUS["last_training_time"] = datetime.datetime.now().isoformat()
        TRAINING_STATUS["training_progress"] = "Starting training..."

        logger.info(f"Starting background training for project {project_id}")

        # Extract zip file to temporary directory
        dataset_dir = extract_zip_to_temp_dir(zip_content)
        logger.info(f"Extracted dataset to: {dataset_dir}")

        # List contents of dataset directory for debugging
        import os

        for root, dirs, files in os.walk(dataset_dir):
            logger.info(f"Directory: {root}")
            logger.info(f"  Subdirs: {dirs}")
            logger.info(f"  Files: {files[:10]}")  # Limit to first 10 files

        TRAINING_STATUS["training_progress"] = "Preparing dataset..."

        # Create dataset and dataloader
        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        dataset = datasets.ImageFolder(root=dataset_dir, transform=transform)
        logger.info(f"Dataset created with {len(dataset)} samples")
        logger.info(f"Dataset classes: {dataset.classes}")

        if len(dataset) == 0:
            logger.error("No training data found in the uploaded ZIP file")
            TRAINING_STATUS["is_training"] = False
            TRAINING_STATUS["training_progress"] = "Failed: No training data found"
            return

        if len(dataset.classes) == 0:
            logger.error("No class directories found in the dataset")
            TRAINING_STATUS["is_training"] = False
            TRAINING_STATUS["training_progress"] = "Failed: No class directories found"
            return

        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

        # Initialize model with correct number of classes and class names
        num_classes = len(dataset.classes)
        class_names = dataset.classes
        logger.info(f"Initializing model with {num_classes} classes: {class_names}")
        model = ResNetImageClassificactionMLModel(
            num_classes=num_classes, class_names=class_names
        )

        TRAINING_STATUS["training_progress"] = (
            f"Training model with {num_classes} classes..."
        )

        # Train model
        trainer = pl.Trainer(
            max_epochs=10,
            accelerator="auto",
            enable_progress_bar=True,
            enable_model_summary=True,
        )
        logger.info("Starting model training...")
        trainer.fit(model, dataloader)
        logger.info("✅ Model training completed successfully!")

        TRAINING_STATUS["training_progress"] = "Saving model weights..."

        # Save trained model weights using the model's method
        try:
            weights_filename = f"project_{project_id}_weights.pth"
            saved_path = model.save_weights(weights_filename)
            logger.info(f"✅ Model weights saved to: {saved_path}")
        except Exception as save_error:
            logger.error(f"Error saving model weights: {save_error}")
            # Fallback: save as checkpoint
            model_dir = "/app/model_weights"
            os.makedirs(model_dir, exist_ok=True)
            checkpoint_path = f"{model_dir}/project_{project_id}_checkpoint.ckpt"
            trainer.save_checkpoint(checkpoint_path)
            logger.info(f"✅ Model checkpoint saved to: {checkpoint_path}")

        # Update global MODEL to the newly trained one
        logger.info("Updating global MODEL instance...")
        MODEL = model
        logger.info("✅ Global MODEL updated with newly trained model")

        # Update training status
        TRAINING_STATUS["is_training"] = False
        TRAINING_STATUS["training_progress"] = (
            f"Completed successfully for {num_classes} classes"
        )
        TRAINING_STATUS["last_training_time"] = datetime.datetime.now().isoformat()

        logger.info(f"🎉 Training completed successfully for project {project_id}")
        logger.info(
            f"📊 Model trained on {len(dataset)} samples with {num_classes} classes"
        )

        # Clean up temporary directory
        import shutil

        shutil.rmtree(dataset_dir)
        logger.info("🧹 Cleaned up temporary files")

    except Exception as e:
        logger.error(
            f"❌ Error during background training for project {project_id}: {str(e)}"
        )
        TRAINING_STATUS["is_training"] = False
        TRAINING_STATUS["training_progress"] = f"Failed: {str(e)}"
        import traceback

        traceback.print_exc()


@app.middleware("http")
async def log_request_data(request: Request, call_next):
    logger.debug("Request headers: %s", request.headers)
    logger.debug("Request body: %s", await request.body())
    response = await call_next(request)
    logger.debug("Response status: %s", response.status_code)
    logger.debug("Response headers: %s", response.headers)
    return response


@app.post("/setup")
async def setup():
    global MODEL

    model_version = MODEL.get_version()
    return JSONResponse(
        {"model_version": model_version, "task_type": "IMAGE_CLASSIFICATION"}
    )


@app.get("/health")
@app.get("/")
async def health():
    global MODEL

    return JSONResponse({"status": "UP", "model_class": MODEL.get_name()})


@app.post("/predict")
async def predict(file: UploadFile):
    """Main prediction endpoint that accepts file uploads."""
    global MODEL

    try:
        logger.info("Received prediction request:")
        logger.info(f"  filename: {file.filename}")
        logger.info(f"  content_type: {file.content_type}")
        logger.info(f"  size: {file.size if hasattr(file, 'size') else 'unknown'}")

        if not file.filename:
            logger.error("No filename provided")
            raise HTTPException(status_code=400, detail="No file provided")

        if not file.content_type:
            logger.error("No content type provided")
            raise HTTPException(status_code=400, detail="No content type provided")

        if not file.content_type.startswith("image/"):
            logger.error(f"Invalid content type: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"File must be an image, got: {file.content_type}",
            )

        image_bytes = await file.read()
        logger.info(f"Read {len(image_bytes)} bytes from uploaded file")

        if len(image_bytes) == 0:
            logger.error("Empty file received")
            raise HTTPException(status_code=400, detail="Empty file received")

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            logger.info(f"Successfully opened image: {image.size}")
        except Exception as img_error:
            logger.error(f"Failed to open image: {img_error}")
            raise HTTPException(
                status_code=400, detail=f"Invalid image file: {str(img_error)}"
            )

        try:
            predicted_class, confidence = MODEL.predict(image)
            logger.info(
                f"Prediction successful: {predicted_class} (confidence: {confidence:.3f})"
            )
        except Exception as pred_error:
            logger.error(f"Model prediction failed: {pred_error}")
            raise HTTPException(
                status_code=500, detail=f"Model prediction failed: {str(pred_error)}"
            )

        return JSONResponse(
            {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "filename": file.filename,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/train")
async def train(
    background_tasks: BackgroundTasks,
    dataset_file: UploadFile,
    project_id: str = Form(...),
    project_name: str = Form(...),
):
    """Train a model with the uploaded dataset."""
    global TRAINING_STATUS

    try:
        logger.info("Received training request:")
        logger.info(f"  dataset_file: {dataset_file.filename}")
        logger.info(f"  project_id: {project_id}")
        logger.info(f"  project_name: {project_name}")

        # Check if already training
        if TRAINING_STATUS["is_training"]:
            raise HTTPException(
                status_code=409,
                detail="Training is already in progress. Please wait for current training to complete.",
            )

        if not dataset_file.filename or not dataset_file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")

        # Read the uploaded file content
        file_content = await dataset_file.read()
        logger.info(f"Read {len(file_content)} bytes from uploaded file")

        # Initialize training status
        TRAINING_STATUS["is_training"] = True
        TRAINING_STATUS["training_progress"] = "Initializing training..."
        TRAINING_STATUS["last_training_time"] = datetime.datetime.now().isoformat()

        # Start background training
        background_tasks.add_task(
            train_model_background, project_id, project_name, file_content
        )

        logger.info(f"🚀 Training task queued for project {project_id}")

        return JSONResponse(
            status_code=200,
            content={
                "message": "Training started successfully",
                "project_id": project_id,
                "project_name": project_name,
                "status": "training",
                "training_progress": TRAINING_STATUS["training_progress"],
                "started_at": TRAINING_STATUS["last_training_time"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        TRAINING_STATUS["is_training"] = False
        TRAINING_STATUS["training_progress"] = f"Failed to start: {str(e)}"
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/status")
async def model_status():
    global MODEL, TRAINING_STATUS

    try:
        model_info = MODEL.get_training_status()
        weights_info = MODEL.get_weights_directory_info()

        return JSONResponse(
            {
                "model_info": model_info,
                "training_status": {
                    "is_training": TRAINING_STATUS["is_training"],
                    "last_training_time": TRAINING_STATUS["last_training_time"],
                    "progress": TRAINING_STATUS["training_progress"],
                    "weights_directory": TRAINING_STATUS["weights_dir"],
                },
                "weights_info": weights_info,
                "available_weights": len(weights_info.get("weight_files", [])),
                "latest_weights": weights_info.get("latest_weight_file"),
                "current_model_classes": getattr(MODEL, "num_classes", "unknown"),
                "class_names": getattr(MODEL, "class_names", []),
            }
        )
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        return JSONResponse(
            {
                "error": str(e),
                "training_status": TRAINING_STATUS,
                "model_available": False,
            },
            status_code=500,
        )


@app.get("/training/progress")
async def get_training_progress():
    """Get detailed training progress information."""
    global TRAINING_STATUS

    return JSONResponse(
        {
            "is_training": TRAINING_STATUS["is_training"],
            "progress": TRAINING_STATUS["training_progress"],
            "last_training_time": TRAINING_STATUS["last_training_time"],
            "weights_directory": TRAINING_STATUS["weights_dir"],
            "timestamp": datetime.datetime.now().isoformat(),
        }
    )


@app.post("/model/reload-weights")
async def reload_weights():
    global MODEL
    try:
        result = MODEL.reload_latest_weights()
        return JSONResponse(
            {
                "message": "Weights reloaded successfully",
                "details": result,
                "current_status": MODEL.get_training_status(),
            }
        )
    except Exception as e:
        logger.error(f"Error reloading weights: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reload weights: {str(e)}"
        )


@app.get("/model/weights")
async def list_weights():
    """List all available weight files"""
    try:
        weights_info = MODEL.get_weights_directory_info()
        return JSONResponse(weights_info)
    except Exception as e:
        logger.error(f"Error listing weights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list weights: {str(e)}")


@app.post("/model/load-weights/{filename}")
async def load_specific_weights(filename: str):
    """Load specific weights file by filename"""
    global MODEL
    try:
        weights_dir = MODEL.weights_dir
        filepath = os.path.join(weights_dir, filename)

        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=404, detail=f"Weights file '{filename}' not found"
            )

        if not filename.endswith(".pth"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only .pth files are supported",
            )

        MODEL.load_weights(filepath)

        return JSONResponse(
            {
                "message": f"Successfully loaded weights from {filename}",
                "loaded_weights": filepath,
                "current_status": MODEL.get_training_status(),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading weights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load weights: {str(e)}")


@app.post("/model/cleanup-weights")
async def cleanup_weights(keep_count: int = 5):
    """Clean up old weight files, keeping only the newest N files"""
    try:
        result = MODEL.cleanup_old_weights(keep_count)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error cleaning up weights: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup weights: {str(e)}"
        )
