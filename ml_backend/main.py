import shutil
import tempfile
import threading
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import UploadFile
from model_manager import ModelManager
from PIL import Image

save_weights_dir = Path("model_weights")
save_weights_dir.mkdir(exist_ok=True)

app = FastAPI()
model_manager = ModelManager(save_weights_dir)


@app.post("/predict")
async def predict(file: UploadFile) -> dict:
    if not model_manager.can_predict():
        raise HTTPException(
            status_code=503,
            detail="Model is currently training",
        )

    data = await file.read()
    image = Image.open(BytesIO(data))
    probabilities = model_manager.model.predict(image)

    result = []
    for probs in probabilities:
        instance_result = []
        for idx, confidence in enumerate(probs):
            class_name = (
                model_manager.class_names[idx]
                if idx < len(model_manager.class_names)
                else str(idx)
            )
            instance_result.append(
                {
                    "idx": idx,
                    "class_name": class_name,
                    "confidence": float(confidence),
                },
            )
        result.append(instance_result)

    status = model_manager.get_status()
    return {
        "predictions": result,
        "version": status["version"],
    }


@app.post("/predict-bulk")
async def predict_bulk(files: list[UploadFile]) -> dict:
    if not model_manager.can_predict():
        raise HTTPException(
            status_code=503,
            detail="Model is currently training",
        )

    all_predictions = []
    for file in files:
        data = await file.read()
        image = Image.open(BytesIO(data))
        probabilities = model_manager.model.predict(image)

        file_predictions = []
        for probs in probabilities:
            instance_result = []
            for idx, confidence in enumerate(probs):
                class_name = (
                    model_manager.class_names[idx]
                    if idx < len(model_manager.class_names)
                    else str(idx)
                )
                instance_result.append(
                    {
                        "idx": idx,
                        "class_name": class_name,
                        "confidence": float(confidence),
                    },
                )
            file_predictions.append(instance_result)

        all_predictions.append(
            {
                "filename": file.filename,
                "predictions": file_predictions,
            },
        )

    status = model_manager.get_status()
    return {
        "predictions": all_predictions,
        "version": status["version"],
    }


@app.post("/train")
async def train(file: UploadFile) -> dict:
    if file.filename is None or not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="File must be a zip archive",
        )

    status_data = model_manager.get_status()
    if status_data["status"] == "training":
        raise HTTPException(
            status_code=409,
            detail="Training already in progress",
        )

    temp_dir = tempfile.mkdtemp()
    try:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "training_data.zip"

        data = await file.read()
        _validate_data_received(data)
        zip_path.write_bytes(data)
        _validate_zip_written(zip_path)

        try:
            extract_dir = temp_path / "extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(str(zip_path), str(extract_dir))
        except (OSError, RuntimeError) as e:
            msg = f"Failed to extract ZIP file: {e!s}"
            raise HTTPException(
                status_code=400,
                detail=msg,
            ) from e

        def train_model() -> None:
            try:
                model_manager.train(extract_dir)
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        thread = threading.Thread(target=train_model, daemon=True)
        thread.start()
    except HTTPException:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    else:
        return {"message": "Training started"}


def _validate_data_received(data: bytes) -> None:
    if not data:
        msg = "Empty file received"
        raise HTTPException(
            status_code=400,
            detail=msg,
        )


def _validate_zip_written(zip_path: Path) -> None:
    if not zip_path.exists() or zip_path.stat().st_size == 0:
        msg = "Failed to write ZIP file"
        raise HTTPException(
            status_code=400,
            detail=msg,
        )


@app.get("/status")
async def status() -> dict:
    status_data = model_manager.get_status()
    return {
        "version": status_data["version"],
        "status": status_data["status"],
    }
