# Use Python 3.12 slim image as base for smaller container size
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first to leverage Docker layer caching
# This allows pip install to be cached if requirements.txt hasn't changed
COPY requirements.txt .

# Copy the main application file
COPY main.py .

# Install Python dependencies without caching pip files to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python output is sent straight to terminal without buffering
# This helps with real-time log viewing in Docker
ENV PYTHONUNBUFFERED=1

# Run the Discord Forex Factory notifier application
CMD ["python", "main.py"]