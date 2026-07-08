# Using a slim image because we don't need to waste gigabytes of space
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your uniquely named dependency file first to leverage Docker caching
COPY deps.txt .

# Install the required packages
RUN pip install --no-cache-dir -r deps.txt

# Copy the actual script into the root of the app directory
COPY index.py .

# FastAPI defaults to running on port 8000
EXPOSE 8000

# Spin up the Uvicorn server pointing directly to index.py's app instance
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "0.0.0.0"]
