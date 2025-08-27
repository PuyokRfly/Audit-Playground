# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for slither
RUN apt-get update && apt-get install -y git

# Copy the requirements file into the container at /app
COPY ./app/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install slither-analyzer
RUN pip install slither-analyzer

# Copy the rest of the application's code into the container at /app
COPY ./app /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run uvicorn when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
