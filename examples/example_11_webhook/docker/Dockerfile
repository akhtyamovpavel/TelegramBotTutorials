# Multi-stage build для оптимизации размера образа

FROM python:3.11-slim as builder

WORKDIR /app

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY ../aiogram/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /root/.local

# Обновляем PATH
ENV PATH=/root/.local/bin:$PATH

# Копируем код бота
COPY ../aiogram/bot_webhook.py .

# Создаем пользователя для запуска (безопасность)
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${WEBAPP_PORT:-8000}/health')" || exit 1

# Запуск
CMD ["python", "bot_webhook.py"]
