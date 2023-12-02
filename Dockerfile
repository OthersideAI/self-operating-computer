# Using an official Python runtime as a parent image
FROM python:3.11-slim

# Setting the working directory in the container
WORKDIR /app

# Installing the project requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installing Project and Command-Line Interface
COPY . .
RUN pip install .

# Running the application
CMD ["operate"]
