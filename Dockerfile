FROM python:3.12.3

WORKDIR /app

# Копируем только requirements.txt сначала для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Убедимся, что .env копируется
COPY .env .env

CMD ["python", "run.py"]