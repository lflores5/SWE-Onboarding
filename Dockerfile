# Dockerfile for Support Tickets Microservice

# Use an official Python runtime as a parent image
# We choose a slim version to keep the image size down
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . .

# Expose the port your application listens on (8000 for FastAPI with uvicorn)
EXPOSE 8000

# Define environment variables for production (optional placeholders)
# These should be overridden at runtime with actual values
# NEVER hardcode sensitive values like COSMOS_DB_KEY in production!
ENV COSMOS_DB_ENDPOINT=""
ENV COSMOS_DB_KEY=""
ENV COSMOS_DB_NAME="support"
ENV COSMOS_CONTAINER_NAME="tickets"

# Command to run the application
# FastAPI app is in app/main.py with app instance named 'app'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
