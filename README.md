# FastAPI with MongoDB and Docker

## Prerequisites

Make sure you have the following installed on your system:

- Docker
- Docker Compose

## Project Structure

- `main.py`: Defines the FastAPI routes.
- `database.py`: Configures the connection to MongoDB.
- `Dockerfile`: Instructions to build the Docker image for the FastAPI application.
- `docker-compose.yml`: Defines the services for Docker Compose.
- `requirements.txt`: Lists the Python dependencies.

## Setup and Run

### Step 1: Clone the Repository

### Step 2:run APP with: uvicorn main:app --reload

### Step 4: Build and Run the Docker Containers

With this command: docker-compose up --build -d

### Step 5: Access the API
The FastAPI application will be available at http://localhost:8000.
