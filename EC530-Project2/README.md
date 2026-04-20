# EC530 Project 2
## Event-Driven Image Annotation System (Redis Pub/Sub)

---

## Overview

This project implements a distributed, event-driven image processing pipeline using Redis Pub/Sub.

Instead of direct function calls, independent services communicate asynchronously through events, simulating a real-world microservices architecture.

---

## Key Concepts Demonstrated

- Event-driven architecture
- Redis Pub/Sub messaging
- Decoupled microservices
- Asynchronous processing pipeline
- Logging and observability
- Unit testing with pytest

---

## Architecture

Upload Service
↓ (image.submitted)
Inference Service
↓ (inference.completed)
Annotation Service

---

## Event Flow

1. Upload Service
   Publishes event: image.submitted

2. Inference Service
   Subscribes to image.submitted
   Simulates inference
   Publishes inference.completed

3. Annotation Service
   Subscribes to inference.completed
   Produces final annotation

---

## Project Structure

EC530-Project2/
- services/
  - upload_service.py
  - inference_service.py
  - annotation_service.py
- shared/
  - redis_client.py
  - events.py
  - logger.py
- tests/
  - test_events.py
  - test_annotation_format.py
- logs/
  - project.log
- .env
- README.md

---

## Setup Instructions

Create virtual environment:

python -m venv venv
venv\Scripts\activate

Install dependencies:

pip install redis python-dotenv pytest

---

## Environment Variables

Create a .env file:

REDIS_HOST=your_host
REDIS_PORT=your_port
REDIS_USERNAME=default
REDIS_PASSWORD=your_password

---

## Running the System

Open 3 terminals.

Terminal 1:
python -m services.inference_service

Terminal 2:
python -m services.annotation_service

Terminal 3:
python -m services.upload_service

---

## Expected Output

Upload Service:
Upload Service published: {...}

Inference Service:
INFO | received event
INFO | published inference result

Annotation Service:
INFO | received inference
INFO | final annotation

---

## Logging

Logs are written to:

logs/project.log

Includes timestamps, service names, and events.

---

## Testing

Run:

set PYTHONPATH=.
pytest tests

Expected:
3 passed

---

## Design Decisions

- Services communicate only via Redis
- No direct coupling between components
- Event-driven model improves scalability
- Logging added for observability
- Error handling prevents crashes

---

## Future Improvements

- Add real ML inference
- Add retry logic
- Use Redis Streams
- Dockerize services
- Add CLI interface

---

## Conclusion

This project demonstrates a complete event-driven distributed system using Redis, modeling real-world backend architecture.
