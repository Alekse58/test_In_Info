import hashlib
import imghdr
from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile, HTTPException
import shutil
import os
from ultralytics import YOLO
from fastapi import FastAPI

from db import engine, Base
from queries import create_item, get_items_by_image_id, get_image_path_by_id, check_image, \
    create_image

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
model = YOLO("yolov8n.pt")
# Путь к исполняемому файлу YOLO
YOLO_EXECUTABLE = model


def calculate_image_hash(image_path):
    # Открываем изображение в бинарном режиме и считываем его содержимое
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Вычисляем SHA-256 хеш изображения
    sha256_hash = hashlib.sha256(image_data).hexdigest()
    return sha256_hash


def run_yolo(input_path):
    results = model.predict(source=input_path, save=True, project=UPLOAD_DIR)
    detected_objects = []
    boxes = results[0].boxes
    print(results)
    for box in boxes:
        coordinates = box.xyxy[0].tolist()
        detected_objects.append(coordinates)

    # TODO найти адекватный метод сохранения
    processed_image_path = f"{results[0].save_dir}/{os.path.basename(input_path)}"
    print("yyyyyyyyyyyyyyyyyyyy", processed_image_path)
    return detected_objects, processed_image_path


def is_valid_image_format(file: UploadFile):
    allowed_formats = {"jpeg", "jpg", "png", "bmp", "dng", "mpo", "tif", "tiff", "webp", "pfm"}
    file_format = imghdr.what(file.file)
    return file_format in allowed_formats


async def photo_processing(file_path, hash):
    items = []
    box, path = run_yolo(file_path)
    id_photo, created = await create_image(image_path=file_path, hashed=hash, path=path)
    for result in box:
        coordinates = result
        if coordinates:
            x1, y1, x2, y2 = coordinates
            items.append(coordinates)
            item = await create_item(x1=x1, y1=y1, x2=x2, y2=y2, photo_id=id_photo)
    return id_photo, items


def save_uploaded_image(file: UploadFile, upload_dir: str):
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_path


app = FastAPI()


@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


@app.post("/detect-bounding-box")
async def detect_bounding_box(file: UploadFile):
    if not is_valid_image_format(file):
        raise HTTPException(status_code=400, detail="Invalid image format")

    # Сохранение загруженного изображения
    file_path = save_uploaded_image(file, UPLOAD_DIR)
    # Хеширование фото
    hash = calculate_image_hash(file_path)
    # Получение или создание фотографии по хешу
    id_photo, created = await check_image(image_path=file_path, hashed=hash)
    # Запуск YOLO для обнаружения объектов
    if created:
        id_photo, items = await photo_processing(file_path, hash)
        return {"image_id": id_photo, "items": items}
    else:
        items = await get_items_by_image_id(id_photo)
        return {"image_id": id_photo, "items": items}


@app.post("/detect-with-bounding-box-image")
async def detect_with_bounding_box_image(file: UploadFile):
    if not is_valid_image_format(file):
        raise HTTPException(status_code=400, detail="Invalid image format")

    # Сохранение загруженного изображения
    file_path = save_uploaded_image(file, UPLOAD_DIR)
    # Хеширование фото
    hash = calculate_image_hash(file_path)
    image, created = await check_image(image_path=file_path, hashed=hash)
    # Запуск YOLO для обнаружения объектов
    items = []
    if created:
        id, items = await photo_processing(file_path, hash)
        image_path = await get_image_path_by_id(id)
        return FileResponse(image_path)
    else:
        image_path = await get_image_path_by_id(image)
        return FileResponse(image_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.1", port=8000)
