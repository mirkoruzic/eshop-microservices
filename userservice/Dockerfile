# Build stage
FROM python:3.9-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN apk add --no-cache --virtual .build-deps build-base \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copy the application code
COPY app.py .

# Final stage
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy the installed dependencies from the build stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application code
COPY app.py .

# Expose the port
EXPOSE 5000

# Set the entrypoint command
CMD ["python", "app.py"]
