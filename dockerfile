# Используем официальный образ Python
FROM python:3.12.3-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости проекта
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Указываем переменные окружения
ENV PYTHONUNBUFFERED=1

# Указываем порт, на котором будет работать приложение
EXPOSE 8080

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "${APP_HOST}", "--port", "${APP_PORT}"]