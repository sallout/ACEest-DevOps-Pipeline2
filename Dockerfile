# Use official slim Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_VERSION 1.0.0

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py /app/

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port
EXPOSE 5000

# Run application using Gunicorn for production readiness
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]