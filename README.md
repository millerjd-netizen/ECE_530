\# ECE 530 – Distributed Systems and Applied Software Engineering



This repository contains a complete set of assignments and projects covering core concepts in modern software systems, including APIs, concurrency, databases, messaging systems, and distributed architectures.



\---



\## Repository Structure



\### Assignment 1 – Airport Finder

Implements a simple data lookup system for airport information.



\- File-based querying

\- Data parsing and filtering

\- Command-line interface



\---



\### Assignment 2 – Elevator API

A REST-style API simulating elevator operations.



\- Endpoints for listing elevators, sending requests, and checking status

\- Demonstrates API design principles



\---



\### Assignment 3 – FastAPI with Postman

A web API built using FastAPI and tested with Postman.



\- RESTful API structure

\- Request and response validation

\- API testing workflow



\---



\### Assignment 4 – Concurrency Queue System

Implements task processing using threading and multiprocessing.



\- Matrix-based task generation

\- Thread-based worker queues

\- Process-based worker queues

\- Basic performance comparison



\---



\### Assignment 5 – Smart Home Database

A SQLite-based system for managing IoT-style device data.



\- Table creation and schema handling

\- CRUD operations

\- Data validation



\---



\### Assignment 6 – Pub/Sub Messaging System

A local publish/subscribe system.



\- Publisher-subscriber architecture

\- Topic-based message routing

\- Local broker implementation



\---



\## Project 1 – Natural Language to SQL System



A system that converts natural language into SQL queries safely.



Features:

\- LLM adapter for query generation

\- SQL validation layer to prevent unsafe queries

\- Schema management

\- Query execution engine



Testing:



```bash

pip install -r natural\_llm\_SQL/requirements.txt

cd natural\_llm\_SQL

PYTHONPATH=. pytest

