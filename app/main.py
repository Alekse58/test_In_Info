import datetime
import os
from fastapi import FastAPI, UploadFile
import shutil
import os
from ultralytics import YOLO
import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import SessionLocal, engine
from app.schemas import Greeting

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
model = YOLO("yolov8n.pt")

# Путь к исполняемому файлу YOLO
YOLO_EXECUTABLE = model


def run_yolo(input_path, output_path):
    # Запуск YOLO с помощью subprocess
    results = model.predict(source=input_path)
    # Detection
    for result in results:
        x1 = result.boxes.xyxy[0].tolist()  # box with xyxy format, (N, 4)
        # class_id = result.boxes.cls[0].item()  # cls, (N, 1)
        # print('x1=', x1, 'class=',class_id)
        return x1,  # class_id




class LazyDbInit:
    """
    Create the db schema, just once.
    """
    is_initizalized = False

    @classmethod
    def initialize(cls):
        if not cls.is_initizalized:
            models.Base.metadata.create_all(bind=engine)
            cls.is_initizalized = True


server = FastAPI()


# Dependency
def get_db():
    LazyDbInit.initialize()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@server.get("/", response_model=list[schemas.Greeting])
async def root(db: Session = Depends(get_db)):
    text = str(datetime.datetime.now())
    greeting = Greeting(text=text)
    db_greeting = models.Greeting(**greeting.dict())
    db.add(db_greeting)
    db.commit()
    return db.query(models.Greeting).all()


@server.post("/detect-bounding-box")
async def detect_bounding_box(file: UploadFile):
    # Сохранение загруженного изображения
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    print(file_path)
    # Запуск YOLO для обнаружения объектов
    output_path = os.path.join(UPLOAD_DIR, "output.jpg")
    box = run_yolo(file_path, output_path)

    results = [{"coordinates": [box]}]
    return results


@server.post("/detect-with-bounding-box-image")
async def detect_with_bounding_box_image(file: UploadFile):
    # Сохранение загруженного изображения
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Запуск YOLO для обнаружения объектов
    output_path = os.path.join(UPLOAD_DIR, "output.jpg")
    run_yolo(file_path, output_path)

    # Отправка изображения с разметкой bounding box
    with open(output_path, "rb") as f:
        image_data = f.read()

    return {"image": image_data}


if __name__ == "__main__":
    import uvicorn

    print("dsaadsdsa")
    uvicorn.run(server, host="0.0.0.0", port=8000)
