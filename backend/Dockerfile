# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install system dependencies required for some Python packages
# and for installing solc
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install solc-select and a specific version of solc
# This ensures the Solidity compiler is available in the environment
RUN solc-select install 0.8.20 && \
    solc-select use 0.8.20 && \
    # Add the solc binary to the PATH
    ln -s /root/.solc-select/artifacts/solc-0.8.20/solc-0.8.20 /usr/local/bin/solc

# Copy the rest of the backend application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# Use --host 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
