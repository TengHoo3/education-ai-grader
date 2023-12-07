# # Use Python 3.10 as base image
# FROM python:3.10-alpine

# # Set a working directory inside the container
# WORKDIR /app

# # Copy the requirements file into the Docker container
# COPY requirements.txt .

# # Install required packages
# RUN apk update && \
#     apk add --no-cache ffmpeg libxext libsm mesa-dri-gallium && \
#     pip install --no-cache-dir -r requirements.txt

# # Optional: Set a default command for the container
# CMD ["streamlit", "run", "0_Extract.py"]
# Use Python 3.10 with Debian Bullseye as base image
FROM python:3.10-slim-bullseye

# Set a working directory inside the container
WORKDIR /app

# Copy the requirements file into the Docker container
COPY requirements.txt .

# Install required packages
RUN apt update && \
    apt install -y ffmpeg libsm6 libxext6 poppler-utils && \
    pip install --no-cache-dir -r requirements.txt

# Optional: Set a default command for the container
    CMD ["streamlit", "run", "0_Extract.py"]