EC530 Project 2

Event-Driven Image Annotation System (Redis Pub/Sub)



Overview



This project implements a distributed, event-driven image processing pipeline using Redis Pub/Sub.



Instead of direct function calls, independent services communicate asynchronously through events, simulating a real-world microservices architecture.





Key Concepts Demonstrated



\- Event-driven architecture

\- Redis Pub/Sub messaging

\- Decoupled microservices

\- Asynchronous processing pipeline

\- Logging and observability

\- Unit testing with pytest





Architecture



Upload Service

→ (image.submitted)

Inference Service

→ (inference.completed)

Annotation Service





Event Flow



1\. Upload Service

&#x20;  Publishes event: image.submitted



2\. Inference Service

&#x20;  Subscribes to image.submitted

&#x20;  Simulates inference

&#x20;  Publishes inference.completed



3\. Annotation Service

&#x20;  Subscribes to inference.completed

&#x20;  Produces final annotation





Project Structure



EC530-Project2/

\- services/

&#x20; - upload\_service.py

&#x20; - inference\_service.py

&#x20; - annotation\_service.py

\- shared/

&#x20; - redis\_client.py

&#x20; - events.py

&#x20; - logger.py

\- tests/

&#x20; - test\_events.py

&#x20; - test\_annotation\_format.py

\- logs/

&#x20; - project.log

\- .env

\- README.md





Setup Instructions



Create virtual environment:



python -m venv venv

venv\\Scripts\\activate



Install dependencies:



pip install redis python-dotenv pytest





Environment Variables



Create a .env file:



REDIS\_HOST=your\_host

REDIS\_PORT=your\_port

REDIS\_USERNAME=default

REDIS\_PASSWORD=your\_password





Running the System



Open 3 terminals.



Terminal 1:

python -m services.inference\_service



Terminal 2:

python -m services.annotation\_service



Terminal 3:

python -m services.upload\_service





Expected Output



Upload Service:

Upload Service published: {...}



Inference Service:

INFO | received event

INFO | published inference result



Annotation Service:

INFO | received inference

INFO | final annotation





Logging



Logs are written to:



logs/project.log



Includes timestamps, service names, and events.





Testing



Run:



set PYTHONPATH=.

pytest tests



Expected:

3 passed





Design Decisions



\- Services communicate only via Redis

\- No direct coupling between components

\- Event-driven model improves scalability

\- Logging added for observability

\- Error handling prevents crashes





Future Improvements



\- Add real ML inference

\- Add retry logic

\- Use Redis Streams

\- Dockerize services

\- Add CLI interface





Conclusion



This project demonstrates a complete event-driven distributed system using Redis, modeling real-world backend architecture.

