FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]