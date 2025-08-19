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
from fastapi import FastAPI, Request, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from model import ResNetImageClassificationMLModel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()


MODEL = ResNetImageClassificationMLModel(weights_dir="model_weights")
IS_TRAINING = False


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


async def train_model_background(zip_content: bytes):
    """Train a model in the background with the provided ZIP file content."""
    global MODEL, IS_TRAINING

    try:
        IS_TRAINING = True

        logger.info("Starting training")

        dataset_dir = extract_zip_to_temp_dir(zip_content)
        logger.info(f"Extracted dataset to: {dataset_dir}")

        for root, dirs, files in os.walk(dataset_dir):
            logger.info(f"Directory: {root}")
            logger.info(f"  Subdirs: {dirs}")
            logger.info(f"  Files: {files[:10]}")

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
            IS_TRAINING = False
            return

        if len(dataset.classes) == 0:
            logger.error("No class directories found in the dataset")
            IS_TRAINING = False
            return

        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

        num_classes = len(dataset.classes)
        class_names = dataset.classes
        logger.info(f"Initializing model with {num_classes} classes: {class_names}")
        model = ResNetImageClassificationMLModel(
            num_classes=num_classes, class_names=class_names
        )

        trainer = pl.Trainer(
            max_epochs=10,
            accelerator="auto",
            enable_progress_bar=True,
            enable_model_summary=True,
        )
        logger.info("Starting model training...")
        trainer.fit(model, dataloader)
        logger.info("✅ Model training completed successfully!")

        try:
            weights_filename = "weights.pth"
            saved_path = model.save_weights(weights_filename)
            logger.info(f"✅ Model weights saved to: {saved_path}")
        except Exception as save_error:
            logger.error(f"Error saving model weights: {save_error}")
            # Fallback: save as checkpoint
            model_dir = "/app/model_weights"
            os.makedirs(model_dir, exist_ok=True)
            checkpoint_path = f"{model_dir}/_checkpoint.ckpt"
            trainer.save_checkpoint(checkpoint_path)
            logger.info(f"✅ Model checkpoint saved to: {checkpoint_path}")

        # Update global MODEL to the newly trained one
        logger.info("Updating global MODEL instance...")
        MODEL = model
        logger.info("✅ Global MODEL updated with newly trained model")

        IS_TRAINING = True

        logger.info("🎉 Training completed successfully")
        logger.info(
            f"📊 Model trained on {len(dataset)} samples with {num_classes} classes"
        )

        logger.info("🧹 Cleaned up temporary files")

    except Exception as e:
        logger.error(f"❌ Error during background training: {str(e)}")
        IS_TRAINING = False

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

        # Get model version
        model_version = MODEL.get_version()

        return JSONResponse(
            {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "filename": file.filename,
                "model_version": model_version,
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
):
    """Train a model with the uploaded dataset."""
    global IS_TRAINING

    try:
        logger.info("Received training request:")
        logger.info(f"  dataset_file: {dataset_file.filename}")

        if IS_TRAINING:
            raise HTTPException(
                status_code=409,
                detail="Training is already in progress. Please wait for current training to complete.",
            )

        if not dataset_file.filename or not dataset_file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")

        file_content = await dataset_file.read()
        logger.info(f"Read {len(file_content)} bytes from uploaded file")

        IS_TRAINING = True

        background_tasks.add_task(train_model_background, file_content)

        return JSONResponse(
            status_code=200,
            content={"message": "Training started successfully"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        IS_TRAINING = False
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_training_progress():
    """Get detailed training progress information."""
    global TRAINING_STATUS

    return JSONResponse(
        {
            "is_training": IS_TRAINING,
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
