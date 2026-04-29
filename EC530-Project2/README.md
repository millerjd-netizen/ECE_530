# EC530 Project 2: Event-Driven Image Processing Pipeline

## Overview
This project implements a distributed, event-driven image processing pipeline using modern data engineering and machine learning concepts.

Upload Service → Inference Service → Annotation Service

## Architecture
- Upload Service: simulates image ingestion
- Inference Service: generates labels and confidence
- Annotation Service:
  - creates annotations
  - generates embeddings
  - stores vectors in FAISS
  - saves metadata to MongoDB

## Technologies
- Redis (Pub/Sub)
- MongoDB (Document DB)
- FAISS (Vector DB)
- NumPy / Pillow
- Pytest

## Data Flow
1. Image uploaded (simulated)
2. Inference assigns label + confidence
3. Annotation service:
   - generates embedding
   - stores in FAISS
   - saves to MongoDB

## Features
- Simulation (random images)
- Embeddings (image → vector)
- FAISS similarity search
- MongoDB storage
- Event-driven architecture

## Setup

Install dependencies:
pip install -r requirements.txt
pip install faiss-cpu pymongo numpy

Start Redis:
redis-server

Start MongoDB (optional):
mongod

## Run Services

python services/upload_service.py
python services/inference_service.py
python services/annotation_service.py

## Run Tests

pytest

Expected:
3 passed

## Requirements Coverage

- Pub/Sub (Redis): YES
- Document DB (MongoDB): YES
- Simulation: YES
- Embeddings: YES
- FAISS (A-level): YES

## Author
Joseph Miller
Boston University EC530