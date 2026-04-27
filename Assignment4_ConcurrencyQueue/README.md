# Assignment 4: Concurrency Queue System

## Overview
This project implements a configurable queue system for processing API-style requests using Python concurrency.

The simulated API task is matrix multiplication using `numpy.matmul()`.

## Features
- Configurable queue size
- Multi-threaded implementation
- Multi-process implementation
- Load testing
- Unit tests

## Structure
Assignment4_ConcurrencyQueue/
├── src/
├── tests/
├── results/
├── requirements.txt
└── README.md

## Install
pip install -r requirements.txt

## Run Threaded Version
python -m src.thread_queue

## Run Process Version
python -m src.process_queue

## Run Load Test
python -m src.load_test

## Run Tests
pytest
