FROM python:3.10

# Установите рабочую директорию
WORKDIR /app

# Копируйте зависимости в контейнер
COPY requirements.txt .

RUN pip install --upgrade pip

# Установите зависимости
RUN pip install -r requirements.txt
RUN pip install opencv-python
RUN pip install python-multipart
RUN pip install alembic
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
# Копируйте исходный код приложения в контейнер
COPY . .
CMD [ "./app_entrypoint.sh" ]
# Укажите команду для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

