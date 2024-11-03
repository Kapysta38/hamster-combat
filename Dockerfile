# Используем образ Python
FROM python:3.9

# Создаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Копируем остальные файлы
COPY . .

# Открываем порт
EXPOSE 3000

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
