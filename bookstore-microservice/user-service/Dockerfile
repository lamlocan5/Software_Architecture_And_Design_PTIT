FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "find app/migrations -name '*.py' ! -name '__init__.py' -delete && python manage.py makemigrations app && until python manage.py migrate; do echo 'Waiting for MySQL...' && sleep 3; done && python manage.py runserver 0.0.0.0:8000"]
