# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем метаданные
LABEL maintainer="Ball Game"
LABEL description="Игра про шарики с графическим интерфейсом"

# Устанавливаем системные зависимости для X11 и pygame
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libfreetype6-dev \
    x11-apps \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения для X11
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы приложения
COPY gui.py .
COPY logic.py .

# Устанавливаем точку входа
ENTRYPOINT ["python", "gui.py"]

# Альтернативный способ запуска (если нужно передать аргументы)
# CMD ["python", "gui.py"]

